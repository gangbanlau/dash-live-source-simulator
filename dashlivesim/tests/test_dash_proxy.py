# The copyright in this software is being made available under the BSD License,
# included below. This software may be subject to other third party and contributor
# rights, including patent rights, and no such rights are granted under this license.
#
# Copyright (c) 2015, Dash Industry Forum.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#  * Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation and/or
#  other materials provided with the distribution.
#  * Neither the name of Dash Industry Forum nor the names of its
#  contributors may be used to endorse or promote products derived from this software
#  without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS AS IS AND ANY
#  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
#  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.

import unittest, sys

from dash_test_util import *
from ..dashlib import dash_proxy

from dash_test_util import *

def findAllIndexes(needle, haystack):
    """Find the index for the beginning of each occurrence of ``needle`` in ``haystack``. Overlaps are allowed."""
    indexes = []
    last_index = haystack.find(needle)
    while -1 != last_index:
        indexes.append(last_index)
        last_index = haystack.find(needle, last_index + 1)
    return indexes

class TestMPDProcessing(unittest.TestCase):
    "Test of MPD parsing"

    def testMPDhandling(self):
        urlParts = ['pdash', 'testpic', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=0)
        d = dp.handle_request()
        self.assertTrue(d.find("<BaseURL>http://streamtest.eu/pdash/testpic/</BaseURL>") > 0)

    def testMPDwithStart(self):
        testOutputFile = "start.mpd"
        rm_outfile(testOutputFile)
        urlParts = ['pdash', 'start_1200', 'testpic', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=0)
        d = dp.handle_request()
        self.assertTrue(d.find('availabilityStartTime="1970-01-01T00:20:00Z"') > 0)
        write_data_to_outfile(d, testOutputFile)

    def testMPDwithStartHasPresentationTimeOffset(self):
        testOutputFile = "pto.mpd"
        rm_outfile(testOutputFile)
        urlParts = ['pdash', 'start_1200', 'testpic', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=0)
        d = dp.handle_request()
        self.assertTrue(d.find('presentationTimeOffset="1200"') > 0)
        write_data_to_outfile(d, testOutputFile)

    def testMPDwithStartandDur(self):
        urlParts = ['pdash', 'start_1200', 'dur_600', 'testpic', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=900)
        d = dp.handle_request()
        if dash_proxy.PUBLISH_TIME:
            self.assertTrue(d.find('publishTime="1970-01-01T00:15:00Z"') > 0)
        self.assertTrue(d.find('availabilityEndTime="1970-01-01T00:30:00Z"') > 0)

    def testMPDwithStartand2Durations(self):
        urlParts = ['pdash', 'start_1200', 'dur_600', 'dur_300', 'testpic', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=900)
        d = dp.handle_request()
        if dash_proxy.PUBLISH_TIME:
            self.assertTrue(d.find('publishTime="1970-01-01T00:15:00Z"') > 0)
        self.assertTrue(d.find('availabilityEndTime="1970-01-01T00:30:00Z"') > 0)
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=1795)
        d = dp.handle_request()
        if dash_proxy.PUBLISH_TIME:
            self.assertTrue(d.find('publishTime="1970-01-01T00:29:00Z"') > 0)
        self.assertTrue(d.find('availabilityEndTime="1970-01-01T00:35:00Z"') > 0)

    def testInit(self):
        urlParts = ['pdash', 'testpic', 'A1', 'init.mp4']
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=0)
        d = dp.handle_request()
        self.assertEqual(len(d), 617)

    def testMediaSegment(self):
        testOutputFile = "t1.m4s"
        rm_outfile(testOutputFile)
        now = 1356998460
        segment = "%d.m4s" % ((now-60)/6)
        urlParts = ['pdash', 'tfdt_32', 'testpic', 'A1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        write_data_to_outfile(d, testOutputFile)

    def testMediaSegmentTooEarly(self):
        urlParts = ['pdash', 'testpic', 'A1', '11.m4s']
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=34)
        d = dp.handle_request()
        self.assertEqual(d['ok'], False)

    def testMediaSegmentBeforeTimeShiftBufferDepth(self):
        now = 1356999060
        segment = "%d.m4s" % ((now-330)/6)
        urlParts = ['pdash', 'testpic', 'A1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        self.assertEqual(d['ok'], False)

    def testLastMediaSegment(self):
        urlParts = ['pdash', 'start_1200', 'dur_600', 'dur_300', 'testpic', 'A1', '349.m4s']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=2102)
        d = dp.handle_request()
        #print "LMSG at %d" % d.find("lmsg")
        self.assertEqual(d.find("lmsg"), 24)

    def testMultiPeriod(self):
        testOutputFile = "multiperiod.mpd"
        rm_outfile(testOutputFile)
        urlParts = ['pdash', 'periods_10', 'testpic', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=3602)
        d = dp.handle_request()
        write_data_to_outfile(d, testOutputFile)
        periodPositions = findAllIndexes("<Period", d)
        self.assertEqual(len(periodPositions), 3)

    def testUtcTiming(self):
        "Test that direct and head works."
        urlParts = ['pdash', 'utc_direct-head', 'testpic', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=0)
        d = dp.handle_request()
        head_pos = d.find('<UTCTiming schemeIdUri="urn:mpeg:dash:utc:http-head:2014" value="http://streamtest.eu/dash/time.html" />')
        direct_pos = d.find('<UTCTiming schemeIdUri="urn:mpeg:dash:utc:direct:2014"')
        self.assertLess(direct_pos, head_pos)

class TestMorePathLevels(unittest.TestCase):
    "Test when representations are further down in"

    def testMPDGet(self):
        urlParts = ['pdash', 'testpic', 'Manifest2l.mpd']
        dp = dash_proxy.DashProvider("streamtest.eu", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=0)
        d = dp.handle_request()
        self.assertGreater(d.find("<BaseURL>http://streamtest.eu/pdash/testpic/</BaseURL>"), 0)

    def testInit(self):
        urlParts = ['pdash', 'testpic', 'en', 'A1', 'init.mp4']
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=0)
        d = dp.handle_request()
        self.assertEqual(len(d), 617)

    def testMediaSegment(self):
        testOutputFile = "t2.m4s"
        rm_outfile(testOutputFile)
        now = 1356998460
        segment = "%d.m4s" % ((now-60)/6)
        urlParts = ['pdash', 'testpic', 'en', 'A1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        write_data_to_outfile(d, testOutputFile)

class TestTfdt(unittest.TestCase):
    "Test that the tfdt rewrite is working correctly"

    def testMediaSegment(self):
        testOutputFile = "tfdt.m4s"
        rm_outfile(testOutputFile)
        now = 1356998460
        segment = "%d.m4s" % ((now-60)/6)
        urlParts = ['pdash', 'testpic', 'A1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        write_data_to_outfile(d, testOutputFile)

    def testTfdtValueFromZero(self):
        "Tfdt value = mediaPresentationTime which corresponds to segmentNr*duration"
        now = 1393936560
        segNr = 232322749
        segment = "%d.m4s" % segNr
        urlParts = ['pdash', 'testpic', 'V1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        tfdtValue = dp.new_tfdt_value
        presentationTime = tfdtValue/15360
        segmentTime = segNr*6
        self.assertEqual(presentationTime, segmentTime)

    def testTfdtValueFromNonZeroAST(self):
        "Tfdt value = mediaPresentationTime which corresponds to segmentNr*duration"
        now = 1393936560
        segNr = 232322749
        ast = now - (now % 10800)
        segment = "%d.m4s" % segNr
        urlParts = ['pdash', 'tfdt_32', 'testpic', 'V1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        tfdtValue = dp.new_tfdt_value
        presentationTime = ast + tfdtValue/15360
        segmentTime = segNr*6
        self.assertEqual(presentationTime, segmentTime)

    def testThatNoPresentationTimeOffsetForTfdt32(self):
        now = 1393936560
        segNr = 232322749
        urlParts = ['pdash', 'tfdt_32', 'testpic', 'V1', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        self.assertFalse(d.find('presentationTimeOffset') > 0)


class TestInitMux(unittest.TestCase):

    def testInitMux(self):
        testOutputFile = "test_mux_init.mp4"
        rm_outfile(testOutputFile)
        now = 1356998460
        urlParts = ['pdash', 'testpic', 'V1__A1', "init.mp4"]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        write_data_to_outfile(d, testOutputFile)

    def testMediaMux(self):
        testOutputFile = "test_mux.m4s"
        rm_outfile(testOutputFile)
        now = 1356998460
        segment = "%d.m4s" % ((now-60)/6)
        urlParts = ['pdash', 'testpic', 'V1__A1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        write_data_to_outfile(d, testOutputFile)

class TestScte35Manifest(unittest.TestCase):

    def setUp(self):
        now = 1356998460
        urlParts = ['pdash', 'scte35_1', 'testpic', 'Manifest.mpd']
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        self.mpd = dp.handle_request()

    def test_scte35_profile_presence(self):
        self.assertTrue(self.mpd.find(",http://dashif.org/guidelines/adin/app") > 0)

    def test_inband_stream_signal(self):
        self.assertTrue(self.mpd.find('<InbandEventStream schemeIdUri="urn:scte:scte35:2013:xml"') > 0)


class TestScte35Segments(unittest.TestCase):

    def testScte35Event(self):
        testOutputFile = "seg_scte35.m4s"
        rm_outfile(testOutputFile)
        segDur = 6
        segNr = 1800000
        now =  segNr*segDur+50
        segment = "%d.m4s" % segNr
        urlParts = ['pdash', 'scte35_3', 'testpic', 'V1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        self.assertEqual(d.find('emsg'), 28)
        write_data_to_outfile(d, testOutputFile)

    def testNoScte35Event(self):
        segDur = 6
        segNr = 1800001
        now =  segNr*segDur+50
        segment = "%d.m4s" % segNr
        urlParts = ['pdash', 'scte35_1', 'testpic', 'V1', segment]
        dp = dash_proxy.DashProvider("127.0.0.1", urlParts, None, VOD_CONFIG_DIR, CONTENT_ROOT, now=now)
        d = dp.handle_request()
        self.assertEqual(d.find('emsg'), -1)

