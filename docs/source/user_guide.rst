User Guide
=================================================================

Welcome to the precision toxicology metadata manager user guide.
In this documentation, we will show you how to generate a spreadsheet for your sample exposition and collection, how
to validate your metadata and how to send them to the University of Birmingham.

--------------------
 Create an account
--------------------
Head to https://ptmm.netlify.app/login and click on "Need a new account? Create one here" link.
Fill in the form with a username, an email address, a password and the organisation you belong to.

.. container:: img-block

    .. image:: ./_static/img/user_guide/login.png
        :align: center
        :alt: Login page
        :class: inline

    .. image:: ./_static/img/user_guide/create_account.png
        :align: center
        :alt: Login page
        :class: inline

    **Figure 1:** Login page (left) and create account page (right)

You will receive an email with further instructions. Click the link to confirm your account and you will be able to
login. Wait for an admin to validate your account and you will be able to use the application.

----------------------------------------------
 Generate your sample collection spreadsheet
----------------------------------------------
The metadata stored by the tool are essential for downstream analysis and deposition to public repositories. The tool
starts by generating information about the sample collection based on a predetermined study design.

After login in, head to https://ptmm.netlify.app/files/create. The form contains 3 pages that will ask you to provide
information about general aspects of your study, timepoints and chemical exposure.

.. container:: img-block

    .. image:: ./_static/img/user_guide/creator_p1.png
        :align: center
        :alt: Creating a new sample collection spreadsheet - General information

    **Figure 2:** Creating a new sample collection spreadsheet - General information

The first page of the creator will ask general information about your sample collection:

#. The consortium partner for which the spreadsheet should be generated. By default, it is the organisation you belong to.
#. The organism you are working on. You can choose between Danio Rerio, Homo Sapiens (HepG2 cells), Xenopus Laevis, Caenorhabditis Elegans, Daphnia Magna and Drosophila Melanogaster (Male or Female).
#. The expected start date and end date of the sample collection step: default to today.
#. The exposure batch, in the format of a double capital letter: default to AA.
#. The solvent, either water or DMSO: default to water.
#. The number of empty tube in this batch: minimum 1, maximum 3, default 3.
#. The number of exposed and controlled replicates per time points: minimum 2, no maximum, default 4.


.. container:: img-block

    .. image:: ./_static/img/user_guide/creator_p2.png
        :align: center
        :alt: Creating a new sample collection spreadsheet - Timepoints

    **Figure 3:** Creating a new sample collection spreadsheet - Timepoints

After clicking "Next", you will access the timepoints page where you are asked to provide:

#. the number of collection timepoints after exposure: minimum 1, maximum 10, default 3.
#. the timepoints units: in the case of precision toxicology, it will always be hours.
#. the values of your timespoints: minimum 1, no maximum, default 0, 0, 0. Be careful because the values cannot exceed the end date of the expected timeframe.

.. container:: img-block

    .. image:: ./_static/img/user_guide/creator_p3.png
        :align: center
        :alt: Creating a new sample collection spreadsheet - Exposure Information

    **Figure 4:** Creating a new sample collection spreadsheet - Exposure Information

The last page of the creator will contain information of the chemicals used for the exposure. They are organised in three
groups based on the dose: **BMD10** (Low), **BMD25** (Medium), **10mg/L** (High). Each chemical can only be added to one
group at a time and you will need to create a new batch to test a chemical at a different dose for the same species. At
least one group must contain a chemical for the spreadsheet to be generated but you can add as many chemicals as you want
in each group.

.. container:: img-block

    .. image:: ./_static/img/user_guide/spreadsheet.png
        :align: center
        :alt: Sample collection spreadsheet

    **Figure 5:** The sample collection spreadsheet


Finally click the submit button at the bottom right of the screen to generate the spreadsheet and add the information
to the database. If you filled everything correctly, the excel document will open on google sheets in a new tab.
The document contains two sheets:

#. The first sheet holds information about the samples. It contains:

    * **Grey fields** (pre-filled by the tool): you should not modify them. They are locked in excel but google sheets only supports this feature for google sheets documents.
    * **White fields**: these are they fields you want to fill after or during exposition and collection.
#. The second sheet contains general information that you should not modify.

--------------------------------------
Search and preview files
--------------------------------------
After creating your first excel file, you can navigate to https://ptmm.netlify.app/users/files to see all the spreadsheets
that you have created or that belong to your organisation.

.. container:: img-block

    .. image:: ./_static/img/user_guide/search.png
        :align: center
        :alt: Searching and filtering files

    **Figure 6:** The search files page


.. container:: h3

    1.3.1. Search files


The left side of the page contains a block with filters that you can use to search for a specific file. You can search using
the following filters:

#. **Validated**: this is the status of the files. It indicates if they passed (success), failed (failed) or are still pending validation (No).
#. **Organism**: the organism for which the files were generated.
#. **Chemical**: the chemical used for the exposure.
#. **Batch**: the exposure batch.
#. **Start and end date**: filter all files where the expected start and end date are between the two given dates.


.. container:: h3

    1.3.2. Preview files

Apart from the information you provided during the file creation, each file box also contains the following information:

#. **Filename**: it is generated automatically with the following format: ``<organisation>_<species>_<batch>.xlsx``.
#. **Validated**: the current validation status of the file. Green for success, red for failure and yellow for pending validation.
#. **Author**: the user who created the file.
#. **Shipped**: No if the file has not been shipped yet. If it has been shipped, it will contain the date of shipment.
#. **Received**: No if the file has not been received yet. If it has been received, it will contain the date of reception. Doesn't show if the file has not been shipped yet.

Overing the mouse over a file box will display a list of actions that you can perform on the file. Depending on the file state,
different actions will be available.

.. container:: img-block

    .. image:: ./_static/img/user_guide/overing_card.png
        :align: center
        :alt: Opening the actions menu when overing the mouse over a file box
        :class: inline single-center md

    **Figure 7:**  Opening the actions menu when overing the mouse over a file box

If a file has not been validated yet (or if it failed validation), you will be able to:

#. View and edit the excel file on google sheets.
#. Validate the file. This will run a series of checks on the file and will change the validation status to success or failure.
#. Delete the file. This will remove the file from the database and from the google drive folder.

--------------------------------------
Validation file content
--------------------------------------
Keep editing your file until you are happy with it and then click the validate button. This will run a series of checks
divided into three categories:

#. **Syntactic checks**: this step is automatic and is realised using JSON Schema. It checks that the file contains all the required fields and that the values are of the correct type. Details about the checks can be found here: https://raw.githubusercontent.com/precisiontox/ptox-metadata-manager/main/ptmd/resources/schemas/exposure_information_sheet_schema.json
#. **Identifiers checks**: this step will ensure that the identifiers generated by the tool were not tempered with. This step is realised by comparing the identifiers in the file with the identifiers stored in the database.
#. **Study design checks**: this step will verify that the study design consistency was not tempered with. It will check if the number of samples, the timepoints, the chemicals and the exposure information are correct.

If the validation fails, a report will be generated with a line by line detail of every error, and the validation status
will turn to "failed" and its colour to red.

.. container:: img-block

    .. image:: ./_static/img/user_guide/report.png
        :align: center
        :alt: Validation report for a failed empty file
        :class: inline single-center lg

    **Figure 8:** First line of the validation report for a failed empty file

The validation report is divided in two sections:

#. **Summary**: this section contains a link to the file on google sheets, the total number of errors and the number of lines containing errors.
#. **Report details**: a line by line report of the errors. Each subsection contains the concerned sample identifier and line number as well as the fields having errors and the corresponding error message.

Once a file has been validated, its status will turn to "success" and its colour to green. On overing the mouse over the file box,
a new action will appear to ship the file and the sample box to the University of Birmingham.


.. container:: img-block

    .. image:: ./_static/img/user_guide/ship.png
        :align: center
        :alt: Shipping a file
        :class: inline single-center md

    **Figure 8:** Popup to select the shipping date and ship the file

Clicking the link will open a popup with a widget to selection the shipping date. Once the date is selected, click the
"Ship" button to ship the file. This will lock the file from any further modification and its card will display the
shipping date and the "Received" status.

.. note::
    The shipping date cannot be earlier than the end date of the expected timeframe.


--------------------------------------
Accessing samples by identifier
--------------------------------------
Once the administrators at Birmingham receive the samples, they will mark the file has received through the admin interface.
This will extract the samples data from the file and store them in the database and make them available through the
Rest API. Login in the ReST API will provide an JSON Web Token (jwt) that you can use to authenticate yourself.
Once logged in, you will be able to access these samples by identifiers using the following endpoint:

.. container:: center

    ``https://pretox.isa-tools.org/api/samples/<identifier>``
