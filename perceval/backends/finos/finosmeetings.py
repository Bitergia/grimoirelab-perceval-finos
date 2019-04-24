# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2019 Fintech Open Source Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Maurizio Pillitu <maoo@finos.org>
#     Santiago Dueñas <sduenas@bitergia.com>
#

import csv
import logging
import tempfile

from grimoirelab_toolkit.datetime import (InvalidDateError,
                                          datetime_utcnow,
                                          datetime_to_utc,
                                          str_to_datetime)

from ...backend import (Backend,
                        BackendCommand,
                        BackendCommandArgumentParser)
from ...client import HttpClient

CATEGORY_ENTRY = "finos-meeting-entry"
SEPARATOR = ','
CSV_HEADER = 'email,name,org,githubid,cm_program,cm_title,cm_type,date'
SKIP_HEADER = True
ID_COLUMNS = 'email,name,date,cm_program,cm_title,cm_type'
DATE_COLUMN = 'date'
TIMESTAMP = 'timestamp'
DATE_ISO = 'date_iso_format'

logger = logging.getLogger(__name__)


class FinosMeetings(Backend):
    """FinosMeetings backend for Perceval.

    This class retrieves the entries from a FINOS meetings
    attendance table. This table can be stored remotely or
    in a local file.

    To initialize this class the URI to that table must be
    provided. The `uri` will be set as the origin of the data.

    :param uri: URI pointer to FINOS meeting data
    :param tag: label used to mark the data
    :param archive: archive to store/retrieve items
    """
    version = '0.3.0'

    CATEGORIES = [CATEGORY_ENTRY]

    def __init__(self, uri, tag=None, archive=None):
        super().__init__(uri, tag=tag, archive=archive)
        self.client = None

    def fetch(self, category=CATEGORY_ENTRY):
        """Fetch the rows from the meetings table.

        :param category: the category of items to fetch

        :returns: a generator of entries
        """
        kwargs = {}
        items = super().fetch(category, **kwargs)

        return items

    def fetch_items(self, category, **kwargs):
        """Fetch the entries.

        :param category: the category of items to fetch
        :param kwargs: backend arguments

        :returns: a generator of items
        """
        logger.info("Looking for a meeting table at feed '%s'", self.origin)

        nentries = 0
        nskipped = 0

        entries = self.client.get_entries()

        for item in _parse_entries(entries):
            # Need to pass which columns are IDs to metadata_id static function
            ret = {
                '_id_columns': ID_COLUMNS
            }

            for i, column in enumerate(CSV_HEADER.split(',')):
                value = item[i]
                if isinstance(item[i], str):
                    value = item[i].strip()

                # If it's the date column, parse value and add it as 'timestamp' in the item
                if column == DATE_COLUMN:
                    try:
                        dt = str_to_datetime(value)
                        ret[DATE_ISO] = datetime_to_utc(dt).isoformat()
                        ret[TIMESTAMP] = datetime_to_utc(dt).timestamp()
                    except InvalidDateError:
                        logger.warning("Skipping entry due to wrong date format: '%s'", value)
                        nskipped += 1
                        break

                ret[column.strip()] = value

            if 'timestamp' in ret:
                yield ret
                nentries += 1

        logger.info("Done. %s/%s meeting entries fetched; %s ignored",
                    nentries, nentries + nskipped, nskipped)

    @classmethod
    def has_archiving(cls):
        """Returns whether it supports archiving entries on the fetch process.

        :returns: this backend does not support entries archive
        """
        return False

    @classmethod
    def has_resuming(cls):
        """Returns whether it supports to resume the fetch process.

        :returns: this backend does not supports entries resuming
        """
        return False

    @staticmethod
    def metadata_id(item):
        """Extracts the identifier from a meeting item.

        For each entry, the value will be the concatenation
        '_id_columns' values
        """
        string = ""
        for column in item['_id_columns'].split(','):
            string = string + item[column] + "-"
        return string

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a meeting item.

        This backend only generates one type of item which is
        `finos-meetings-entry`.
        """
        return CATEGORY_ENTRY

    @staticmethod
    def metadata_updated_on(item):
        """Extracts the update time from a FINOS meeting CSV row.

        The timestamp is calculated before and stored into the 'timestamp'
        field extracted from 'published' field.

        :param item: item generated by the backend

        :returns: the timestamp field, UNIX format
        """
        return item['timestamp']

    def _init_client(self, from_archive=False):
        """Init client"""

        return FinosMeetingsClient(self.origin, SEPARATOR, SKIP_HEADER)


def _parse_entries(rows):
    ret = []
    for i, row in enumerate(rows):
        if SKIP_HEADER and i == 0:
            logger.debug("skipping header")
        else:
            ret.append(row)
    return ret


class FinosMeetingsClient(HttpClient):
    """FinosMeetings API client.

    :param uri: URI Pointer to CSV contents
    :param archive: an archive to store/read fetched data
    :param from_archive: it tells whether to write/read the archive
    """
    def __init__(self, uri, archive=None, from_archive=False):
        if uri.startswith('file://'):
            self.file_path = uri.split('file://', 1)[1]
        else:
            self.file_path = tempfile.mkdtemp() + "/perceval-finos-meetings-backend-" + str(datetime_utcnow()) + ".csv"
            super().__init__(uri, archive=archive, from_archive=from_archive)
            response = self.session.get(uri)
            open(self.file_path, 'wb').write(response.content)

    def get_entries(self):
        """Retrieve all entries from a CVS file"""

        self.session = None
        with open(self.file_path, newline='') as csv_content:
            reader = csv.reader(csv_content, delimiter=SEPARATOR)
            rows = []
            for row in reader:
                rows.append(row)
            return rows


class FinosMeetingsCommand(BackendCommand):
    """Class to run FinosMeetings backend from the command line."""

    BACKEND = FinosMeetings

    @classmethod
    def setup_cmd_parser(cls):
        """Returns the FinosMeetings argument parser."""

        parser = BackendCommandArgumentParser(cls.BACKEND.CATEGORIES)

        # Required arguments
        parser.parser.add_argument('uri',
                                   help="URI pointer to FINOS meetings data")

        return parser
