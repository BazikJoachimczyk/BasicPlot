import io
import os
import sys
import tempfile
import unittest
from unittest import mock

import matplotlib
matplotlib.use('Agg')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import create_objects
import newsletter
import plot_all

SAMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'newsletter_sample.txt')


def read_sample():
    with open(SAMPLE, encoding='utf-8') as file:
        return file.read()


class ParseNorthTargetsTests(unittest.TestCase):
    def setUp(self):
        self.targets = newsletter.ParseNorthTargets(read_sample())

    def test_only_north_section(self):
        self.assertEqual([t.name for t in self.targets], [
            'HD216629', 'Gaia_DR3_1647756923141966720', 'GAIA DR3 2207162600835525760',
            'LS I +61 302', 'UCAC4 489-096064', '3C 138', 'SN 2026fov'])
        self.assertTrue(all(t.dec > 0 for t in self.targets))

    def test_row_fields(self):
        t = self.targets[3]
        self.assertEqual(t.name, 'LS I +61 302')
        self.assertAlmostEqual(t.ra, 40.131935)
        self.assertAlmostEqual(t.dec, 61.229332)
        self.assertAlmostEqual(t.mag, 10.8)
        self.assertAlmostEqual(t.sun_separation, 105.0)
        self.assertEqual(t.classification, 'Unknown')
        self.assertEqual(t.description, 'Be-star with unknown compact companion')

    def test_description_with_numbers(self):
        t = self.targets[4]
        self.assertEqual(t.name, 'UCAC4 489-096064')
        self.assertAlmostEqual(t.ra, 289.3155)
        self.assertIn('2.36 days', t.description)

    def test_tabs_replaced_by_spaces(self):
        # e-mail clients often turn tabs into spaces when copying
        targets = newsletter.ParseNorthTargets(read_sample().replace('\t', '   '))
        self.assertEqual([(t.name, t.ra, t.dec) for t in targets],
                         [(t.name, t.ra, t.dec) for t in self.targets])

    def test_windows_line_endings(self):
        targets = newsletter.ParseNorthTargets(read_sample().replace('\n', '\r\n'))
        self.assertEqual(len(targets), 7)

    def test_missing_section(self):
        with self.assertRaisesRegex(ValueError, 'North'):
            newsletter.ParseNorthTargets('Hello,\nnothing here\n')


class SaveTargetsTests(unittest.TestCase):
    def test_round_trip_with_basicplot_input(self):
        targets = newsletter.ParseNorthTargets(read_sample())
        fd, path = tempfile.mkstemp(suffix='.txt')
        os.close(fd)
        self.addCleanup(os.remove, path)
        newsletter.SaveTargets(targets, path)
        loaded = create_objects.BuildObjectsList(path)
        self.assertEqual([(o.name, o.ra, o.dec) for o in loaded],
                         [(t.name, t.ra, t.dec) for t in targets])


class CliTests(unittest.TestCase):
    def run_cli(self, *argv, stdin=None):
        with mock.patch.object(plot_all, 'Plot') as plot, \
             mock.patch('sys.stdout', new_callable=io.StringIO), \
             mock.patch('sys.stdin', io.StringIO(stdin or '')):
            newsletter.run(list(argv))
        return plot

    def test_plots_north_targets(self):
        plot = self.run_cli(SAMPLE, '-moon')
        objects, timescale = plot.call_args.args
        self.assertEqual(len(objects), 7)
        self.assertEqual(len(timescale), 901)
        self.assertTrue(plot.call_args.kwargs['moon_separation'])

    def test_reads_stdin(self):
        plot = self.run_cli('-', '-mode', '12', stdin=read_sample())
        objects, timescale = plot.call_args.args
        self.assertEqual(len(objects), 7)
        self.assertEqual(len(timescale), 720)
        self.assertFalse(plot.call_args.kwargs['moon_separation'])

    def test_not_a_newsletter_exits(self):
        with self.assertRaises(SystemExit):
            self.run_cli('-', stdin='just some text\n')


if __name__ == '__main__':
    unittest.main()
