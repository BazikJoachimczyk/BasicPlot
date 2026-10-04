import json
import os
import sys
import tempfile
import unittest
import warnings
from unittest import mock

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, AltAz, get_body

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings('ignore')   # astropy IERS / ERFA "dubious year" noise

import basicplot
import calculate_visibility
import create_objects
import plot_all
import time_scale
from create_objects import PIWNICE, Object


def write_temp(text):
    f = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    f.write(text)
    f.close()
    return f.name


class TimeScaleTests(unittest.TestCase):
    def check_grid(self, ts, start_iso, end_iso):
        self.assertEqual(ts[0].isot[:16], start_iso)
        self.assertEqual(ts[-1].isot[:16], end_iso)
        steps = np.diff(ts.unix)
        np.testing.assert_allclose(steps, 60, atol=1e-3)

    def test_evening_uses_today(self):
        ts = time_scale.TimeScaleForTheNight(Time('2026-10-04T20:30:00'))
        self.check_grid(ts, '2026-10-04T16:00', '2026-10-05T07:00')

    def test_after_midnight_uses_yesterday(self):
        ts = time_scale.TimeScaleForTheNight(Time('2026-10-05T03:00:00'))
        self.check_grid(ts, '2026-10-04T16:00', '2026-10-05T07:00')

    def test_early_morning_window_still_covers_now(self):
        now = Time('2026-10-05T05:30:00')
        ts = time_scale.TimeScaleForTheNight(now)
        self.assertTrue(ts[0] <= now <= ts[-1])

    def test_winter_night_includes_morning_twilight(self):
        ts = time_scale.TimeScaleForTheNight(Time('2026-12-21T20:00:00'))
        sun = get_body('sun', ts[-1]).transform_to(AltAz(obstime=ts[-1], location=PIWNICE))
        self.assertGreater(sun.alt.deg, -6)    # civil twilight reached before the window ends

    def test_12hrs(self):
        ts = time_scale.TimeScale12hrs(Time('2026-10-04T10:00:00'))
        self.assertEqual(len(ts), 720)
        self.check_grid(ts, '2026-10-04T10:01', '2026-10-04T22:00')


class CreateObjectsTests(unittest.TestCase):
    def test_skips_blank_and_comment_lines(self):
        path = write_temp('# header\nA 10.0 20.0\n\n   \nB 30.5 -40.25\n\n')
        self.addCleanup(os.remove, path)
        objects = create_objects.BuildObjectsList(path)
        self.assertEqual([(o.name, o.ra, o.dec) for o in objects], [('A', 10.0, 20.0), ('B', 30.5, -40.25)])

    def test_name_with_spaces(self):
        path = write_temp('M 31 Andromeda 10.68 41.27\n')
        self.addCleanup(os.remove, path)
        obj = create_objects.BuildObjectsList(path)[0]
        self.assertEqual(obj.name, 'M 31 Andromeda')
        self.assertAlmostEqual(obj.ra, 10.68)

    def test_malformed_line_reports_line_number(self):
        path = write_temp('A 10 20\nbroken\n')
        self.addCleanup(os.remove, path)
        with self.assertRaisesRegex(ValueError, ':2:'):
            create_objects.BuildObjectsList(path)


class VisibilityTests(unittest.TestCase):
    times = Time('2026-10-04T22:00:00') + np.arange(0, 60, 10) * u.min

    def test_polaris_altitude_close_to_latitude(self):
        alts = calculate_visibility.CalculateAltitudes(ra=37.95, dec=89.264, time=self.times)
        np.testing.assert_allclose(alts, 53.1, atol=1.0)

    def test_ui_ra_is_hours(self):
        # Vega: 18h36m56s = 279.233 deg
        with mock.patch('builtins.print'):
            out = json.loads(calculate_visibility.UIAltitudes(
                ra_str='18:36:56', dec_str='+38:47:01', time=self.times,
                lat_str='53:05:51', lon_str='18:33:45'))
        expected = calculate_visibility.CalculateAltitudes(ra=279.233, dec=38.7836, time=self.times)
        np.testing.assert_allclose(out['altitude'], expected, atol=0.05)
        self.assertEqual(out['time'][0], '22:00:00')
        self.assertEqual(len(out['time']), len(self.times))


class TwilightTests(unittest.TestCase):
    def test_contiguous_spans(self):
        t = list(range(8))
        mask = [False, True, True, False, False, True, True, True]
        self.assertEqual(plot_all.ContiguousSpans(t, mask), [(1, 2), (5, 7)])

    def test_contiguous_spans_empty(self):
        self.assertEqual(plot_all.ContiguousSpans([0, 1, 2], [False] * 3), [])

    def test_twilight_spans_missing_band_is_empty(self):
        sun = np.array([5, -3, -8, -3, 5])     # never below -12
        spans = dict(plot_all.TwilightSpans(list(range(5)), sun))
        self.assertEqual(spans['whitesmoke'], [(1, 3)])
        self.assertEqual(spans['lightgray'], [(2, 2)])
        self.assertEqual(spans['darkgray'], [])


class MoonSeparationTests(unittest.TestCase):
    def test_matches_separation_seen_from_observatory(self):
        t = Time('2026-10-04T22:00:00') + np.arange(0, 120, 30) * u.min
        obj = Object('Gaia24bux', 347.4182, 62.4830)
        moon = get_body('moon', t, location=PIWNICE)
        got = plot_all.MoonSeparations(obj, moon)

        frame = AltAz(obstime=t, location=PIWNICE)
        star_altaz = SkyCoord(ra=obj.ra * u.deg, dec=obj.dec * u.deg).transform_to(frame)
        expected = moon.transform_to(frame).separation(star_altaz).deg
        np.testing.assert_allclose(got, expected, atol=0.01)


class PlotSmokeTests(unittest.TestCase):
    objects = [Object('A', 347.4182, 62.4830), Object('B', 281.649375, 0.922556), Object('C', 217.567, 23.062)]

    def run_plot(self, timescale):
        with mock.patch.object(plt, 'show'):
            plot_all.Plot(self.objects, timescale)
        fig = plt.gcf()
        self.addCleanup(plt.close, fig)
        return fig

    def test_summer_night_without_astronomical_darkness(self):
        self.run_plot(time_scale.TimeScaleForTheNight(Time('2026-06-21T22:00:00')))

    def test_daytime_12hrs_without_twilight(self):
        ts = time_scale._minute_grid(Time('2026-10-04T08:00:00'), 60)
        self.run_plot(ts)

    def test_single_panel_with_twilight_shading(self):
        fig = self.run_plot(time_scale.TimeScaleForTheNight(Time('2026-10-04T20:00:00')))
        self.assertEqual(len(fig.axes), 1)
        self.assertGreater(sum(isinstance(p, Rectangle) for p in fig.axes[0].patches), 0)

    def test_legend_has_mean_moon_separation(self):
        ts = time_scale.TimeScaleForTheNight(Time('2026-10-04T20:00:00'))
        fig = self.run_plot(ts)
        labels = [t.get_text() for t in fig.legends[0].get_texts()]
        moon = get_body('moon', ts, location=PIWNICE)
        expected = [f"{i + 1} - {o.name} ({np.mean(plot_all.MoonSeparations(o, moon)):.0f} deg)"
                    for i, o in enumerate(self.objects)]
        self.assertEqual(labels, ['Moon Altitude'] + expected)

    def test_every_target_has_its_own_style(self):
        styles = [plot_all.TargetStyle(i) for i in range(32)]
        self.assertEqual(len(set(styles)), 32)

    def test_target_lines_use_target_styles(self):
        fig = self.run_plot(time_scale.TimeScaleForTheNight(Time('2026-10-04T20:00:00')))
        target_lines = [line for line in fig.axes[0].get_lines() if line.get_label()[0].isdigit()]
        drawn = [(matplotlib.colors.to_hex(line.get_color()), line.get_linestyle()) for line in target_lines]
        self.assertEqual(drawn, [plot_all.TargetStyle(i) for i in range(len(self.objects))])

    def test_legend_label_format(self):
        self.assertEqual(plot_all.LegendLabel(3, Object('Gaia21azc', 0, 0), 24.6), '3 - Gaia21azc (25 deg)')


class CliTests(unittest.TestCase):
    def test_tonight_plots_objects_from_file(self):
        path = write_temp('A 10 20\nB 30 40\n')
        self.addCleanup(os.remove, path)
        with mock.patch.object(plot_all, 'Plot') as plot, mock.patch('builtins.print'):
            basicplot.run(['-mode', 'tonight', '-file', path])
        objects, timescale = plot.call_args.args
        self.assertEqual([o.name for o in objects], ['A', 'B'])

    def test_moon_flag_removed(self):
        with self.assertRaises(SystemExit), mock.patch('sys.stderr'):
            basicplot.run(['-mode', 'tonight', '-file', 'x.txt', '-moon'])


if __name__ == '__main__':
    unittest.main()
