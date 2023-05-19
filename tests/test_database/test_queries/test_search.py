from unittest import TestCase
from unittest.mock import patch

from ptmd.config import app
from ptmd.database import File
from ptmd.database.queries.search import search_files, assemble_integer_clause


class TestSearch(TestCase):

    @patch("ptmd.database.queries.search.File")
    @patch("ptmd.database.queries.search.assemble_integer_clause")
    def test_search_files(self, mock_clause, mock_file):
        mock_file.query.filter().paginate().items = [
            {'timepoints': [{"files": [{"id": 1}, {"id": 2}]}]},
        ]
        mock_file.query.filter().paginate().pages = 2
        mock_file.query.filter().paginate().total = 4
        with app.app_context():
            files = search_files(
                page=2, per_page=2,
                batch='AC', name="A", is_valid=False,
                replicates={'operator': 'ne', 'value': 3},
                controls={'operator': 'gt', 'value': 0},
                blanks={'operator': 'gte', 'value': 2},
                organisation_name="UOB",
                organism_name="Drosophila Me",
                vehicle_name="DMSO",
                chemical_name="Imidazole"
            )
            page = {'current_page': 2, 'next_page': 3, 'previous_previous': 1, 'pages': 2, 'per_page': 2, 'total': 4}
            self.assertEqual(files['pagination'], page)
            self.assertEqual(len(files['data']), 1)

            mock_file.query.filter().paginate().items = [{'timepoints': [{"files": [{"id": 1}, {"id": 2}]}]}]
            files = search_files(
                page=2, per_page=2,
                batch='AC', name="A", is_valid=True,
                replicates={'operator': 'ne', 'value': 3},
                controls={'operator': 'gt', 'value': 0},
                blanks={'operator': 'gte', 'value': 2},
                organisation_name="UOB",
                organism_name="Drosophila Me",
                vehicle_name="DMSO",
                chemical_name="Imidazole"
            )
            page = {'current_page': 2, 'next_page': 3, 'previous_previous': 1, 'pages': 2, 'per_page': 2, 'total': 4}
            self.assertEqual(files['pagination'], page)
            self.assertEqual(len(files['data']), 1)

    def test_assemble_integer_clause(self):
        clause = assemble_integer_clause(
            filter_data={'operator': 'ne', 'value': 3},
            column='replicates',
            target=File
        )
        self.assertEqual(str(clause), "file.replicates != :replicates_1")

        clause = assemble_integer_clause(
            filter_data={'operator': 'gt', 'value': 3},
            column='replicates',
            target=File
        )
        self.assertEqual(str(clause), "file.replicates > :replicates_1")

        clause = assemble_integer_clause(
            filter_data={'operator': 'gte', 'value': 3},
            column='replicates',
            target=File
        )
        self.assertEqual(str(clause), "file.replicates >= :replicates_1")

        clause = assemble_integer_clause(
            filter_data={'operator': 'lt', 'value': 3},
            column='replicates',
            target=File
        )
        self.assertEqual(str(clause), "file.replicates < :replicates_1")

        clause = assemble_integer_clause(
            filter_data={'operator': 'lte', 'value': 3},
            column='replicates',
            target=File
        )
        self.assertEqual(str(clause), "file.replicates <= :replicates_1")

        clause = assemble_integer_clause(
            filter_data={'operator': 'eq', 'value': 3},
            column='controls',
            target=File
        )
        self.assertEqual(str(clause), "file.controls = :controls_1")
