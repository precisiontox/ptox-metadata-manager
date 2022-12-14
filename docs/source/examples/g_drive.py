from os import path

from ptmd import HarvesterInput, GoogleDriveConnector


HERE = path.abspath(path.dirname(__file__))


def test():
    output_path = path.join(HERE, 'test.xlsx')
    exposure_condition = [
        {'chemical_name': 'chemical1', 'doses': ['BMD10', 'BMD25'], 'timepoints': 2},
        {'chemical_name': 'chemical2', 'doses': ['BMD10', 'BMD25'], 'timepoints': 4}
    ]
    harvester = HarvesterInput(partner='KIT',
                               organism="organism1",
                               exposure_conditions=exposure_condition,
                               exposure_batch='AA',
                               replicate4exposure=4,
                               replicate4control=4,
                               replicate_blank=2,
                               start_date='2018-01-01', end_date='2019-01-02')
    harvester.save_file(output_path)
    connector = GoogleDriveConnector()
    file = connector.upload_file(partner={"name1": 'KIT', 'id': None}, file_path=output_path)
    return 'https://docs.google.com/spreadsheets/d/%s' % file['id']


if __name__ == '__main__':
    print(test())
