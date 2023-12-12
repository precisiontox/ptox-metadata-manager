""" Ontology annotations and sources to create the ISA investigations.
"""
from uuid import uuid4

from isatools.model import OntologyAnnotation, OntologySource

# SOURCES
NCBI_TAXON: OntologySource = OntologySource(
    name='NCBITaxon',
    file='http://purl.obolibrary.org/obo/ncbitaxon.owl',
    version='2022-08-18',
    description="NCBI Taxonomy"
)
PATO: OntologySource = OntologySource(
    name='PATO',
    file='http://purl.obolibrary.org/obo/pato.owl',
    version='2022-08-31',
    description="Phenotype and Trait Ontology"
)
NCIT: OntologySource = OntologySource(
    name='NCIT',
    file=' http://purl.obolibrary.org/obo/ncit.owl',
    version='22.07d',
    description="National Cancer Institute Thesaurus"
)
UO: OntologySource = OntologySource(
    name='UO',
    file='http://purl.obolibrary.org/obo/uo.owl',
    description="Units of measurement ontology"
)
CHEBI: OntologySource = OntologySource(
    name='CHEBI',
    file='http://purl.obolibrary.org/obo/chebi/211/chebi.owl',
    description="Chemical Entities of Biological Interest"
)
OBI: OntologySource = OntologySource(
    name='OBI',
    file='http://purl.obolibrary.org/obo/obi/2022-07-11/obi.owl',
    description="Ontology for Biomedical Investigations"
)
BAO: OntologySource = OntologySource(
    name="BAO",
    description="Bioassay Ontology"
)
CHMO: OntologySource = OntologySource(
    name="CHMO",
    description="Chemical Methods Ontology"
)
MS: OntologySource = OntologySource(
    name="PSI-MS",
    description="PSI Mass Spectrometry"
)
MSIO: OntologySource = OntologySource(
    name="MSIO",
    description="Metabolomics Standardisation Initiative Ontology"
)
STATO: OntologySource = OntologySource(
    name="STATO",
    description="Statistics Ontology"
)

# CHARACTERISTICS ONTOLOGY ANNOTATIONS
ORGANISM_OA: OntologyAnnotation = OntologyAnnotation(term_source=NCIT, term='organism', term_accession='NCIT:C14250')
DROSOPHILA_OA: OntologyAnnotation = OntologyAnnotation(
    term_source=NCBI_TAXON, term='Drosophila melanogaster', term_accession='NCBITaxon:7227'
)
MALE_OA: OntologyAnnotation = OntologyAnnotation(term_source=PATO, term='male', term_accession='PATO:0000384')
FEMALE_OA: OntologyAnnotation = OntologyAnnotation(term_source=PATO, term='female', term_accession='PATO:0000383')
SEX_OA: OntologyAnnotation = OntologyAnnotation(term_source=PATO, term='biological sex', term_accession='PATO:0000047')
EXPOSURE_OA: OntologyAnnotation = OntologyAnnotation(term_source=NCIT, term='Exposure', term_accession='NCIT:C17941')
SAMPLING_OA: OntologyAnnotation = OntologyAnnotation(term_source=NCIT, term='Sampling', term_accession='NCIT:C25662')
HOURS_OA: OntologyAnnotation = OntologyAnnotation(term_source=UO, term='hour', term_accession='UO:0000032',
                                                  id_=f"#unit/{uuid4()}")
ORGANISM_NA_OA: OntologyAnnotation = OntologyAnnotation(term_source=NCIT, term='N/A', term_accession='NCIT:C48660')
BOX_OA: OntologyAnnotation = OntologyAnnotation(term_source=NCIT, term='Box', term_accession='NCIT:C43178')
POSITION_OA: OntologyAnnotation = OntologyAnnotation(
    term_source=NCIT, term='Position x and y', term_accession='NCIT:C104788'
)
REPLICATE_OA: OntologyAnnotation = OntologyAnnotation(term_source=NCIT, term='Replicate', term_accession='NCIT:C104789')

# FACTOR VALUES ONTOLOGY ANNOTATIONS
COMPOUND_OA: OntologyAnnotation = OntologyAnnotation(term_source=CHEBI, term='Compound', term_accession='CHEBI:24431')
DOSE_OA: OntologyAnnotation = OntologyAnnotation(term_source=OBI, term="Dose", term_accession='OBI:0000984')
TIMEPOINT_OA: OntologyAnnotation = OntologyAnnotation(term_source=MS, term="Timepoint", term_accession='MS:1001815')

# PROTOCOL TYPE ONTOLOGY ANNOTATIONS
GROWTH_OA: OntologyAnnotation = OntologyAnnotation(term="growth", term_accession="", term_source=OBI)
TREATMENT_OA: OntologyAnnotation = OntologyAnnotation(term="treatment", term_accession="", term_source=OBI)
EXTRACTION_OA: OntologyAnnotation = OntologyAnnotation(term="material separation", term_accession="", term_source=OBI)

# TREATMENT ONTOLOGY ANNOTATIONS
COLLECTION_ORDER_OA: OntologyAnnotation = OntologyAnnotation(
    term="collection order", term_accession="", term_source=OBI
)
EXPOSURE_BATCH_OA: OntologyAnnotation = OntologyAnnotation(term="exposure batch", term_accession="", term_source=OBI)
EXPOSURE_ROUTE_OA: OntologyAnnotation = OntologyAnnotation(term="exposure route", term_accession="", term_source=OBI)
OPERATOR_OA: OntologyAnnotation = OntologyAnnotation(term="operator", term_accession="", term_source=OBI)


# MAPPERS
ONTOLOGY_SOURCES: list = [NCBI_TAXON, PATO, NCIT, UO, CHEBI, BAO, CHMO, MSIO, STATO, OBI, MS]
SPECIES: dict = {
    'Danio_rerio': OntologyAnnotation(term_source=NCBI_TAXON, term='Danio rerio', term_accession='NCBITaxon:7955'),
    'Homo_sapiens_HepG2_cells': OntologyAnnotation(
        term_source=NCBI_TAXON, term='Homo Sapiens', term_accession='NCBITaxon:9606'
    ),
    'Xenopus_laevis': OntologyAnnotation(
        term_source=NCBI_TAXON, term='Xenopus laevis', term_accession='NCBITaxon:8355'
    ),
    'C_elegans': OntologyAnnotation(
        term_source=NCBI_TAXON, term='Caenorhabditis elegans', term_accession='NCBITaxon:6239'
    ),
    'Daphnia_magna': OntologyAnnotation(term_source=NCBI_TAXON, term='Daphnia magna', term_accession='NCBITaxon:35525'),
    'Drosophila_melanogaster': DROSOPHILA_OA,
}
TREATMENT_PARAMETERS = ["collection_order", "exposure_batch", "exposure_route", "operator"]
