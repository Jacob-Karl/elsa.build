# Stdlib imports
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from shutil import copyfile
from .chocolate import *
import datetime
from lxml import *
from bs4 import BeautifulSoup

#    Final Variables
MAX_CHAR_FIELD = 100
MAX_LID_FIELD = 255
MAX_TEXT_FIELD = 1000

PDS4_LABEL_TEMPLATE_DIRECTORY = os.path.join(settings.TEMPLATE_DIR, 'pds4_labels')

#    Final Variables
#       --- These will be changed when Version model object gets complete ---
MODEL_LOCATION = "http://pds.nasa.gov/pds4/schema/released/pds/v1/PDS4_PDS_1800.sch"
NAMESPACE = "{http://pds.nasa.gov/pds4/pds/v1}"
SCHEMA_INSTANCE = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMA_LOCATION = "http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/schema/released/pds/v1/PDS4_PDS_1800.xsd"



#    Helpful functions here
def get_most_current_version():
    # Get all versions listed in ELSA
    Version_List = Version.objects.all()

    if Version_List:
        # Find the highest version number

        highest_number = 0

        for version in Version_List:
            if version.number > highest_number:
                highest_number = version.number
                highest_version = version

            # Now that we have iterated through the list, the highest number should be obtained
            return highest_version
    else:
        return 0

def get_upload_path(instance, filename):
    return '{0}/{1}'.format(instance.user.id, filename)

def get_three_years_in_future():
    now = datetime.datetime.now()
    return now.year + 3

def get_user_document_directory(instance, filename):
    document_collection_directory = 'archive/{0}/{1}/documents/'.format(instance.bundle.user.username, instance.bundle.name)
    return document_collection_directory



#    Register your models here 
@python_2_unicode_compatible
class Version(models.Model):

    number = models.CharField(max_length=4)
    xml_schema = models.CharField(max_length=MAX_CHAR_FIELD)

    # Accessors - NONE

    # Cleaners
    """
        with_dots gives the version number with dots between each number.  Sometimes in PDS4
        we require that the number include dots, other times not so much.
    """
    def with_dots(self):
        version_number = self.number
        new_number = ''

        # Add a period after each digit.  Ex: 1234 -> 1.2.3.4.
        for each_digit in version_number:
            new_number = '{0}{1}{2}'.format(new_number, each_digit, '.')

        # Remove the last period. Ex: 1.2.3.4. -> 1.2.3.4
        new_number = new_number[:-1]

        # Number is now formatted to pds standard, so return it.
        return new_number


    # Meta
    def __str__(self):
        return self.number

    # Validators
    def get_validators(self):
        pass

    # Main Functions
    def version_update(self, version, inFile):

	i=0
	j=0
	

	#read the bundle and collection files and store their contents in strings.
	#If the file is invalid a statement will be printed and the function will quit.
	try:
		fil = open(inFile,'r')

		fileText = fil.read()

		fil.close()
	except:
		print inFile + " is an invalid file"
		return

	#change the version number
	while i<2:
	    chunk = fileText[j:j+4]
	    #if a new version is introduced this line will need to be changed
	    if chunk == "1700" or chunk == "1800" or chunk == "1900" or chunk == "1A00":
		i+=1
		fileText = list(fileText)
		fileText[j+1] = str(version)[1]
		fileText = "".join(fileText)
	    j+=1
	    #prevents the while loop from looping infinately should the if statement fail
	    if j>len(fileText):
		print "No valid version number found. If product_bundle.xml and product_collection.xml contain valid version numbers check the conditional in versionModelObject."
		break

	#write the new bundle and collection to the xmls
	fil = open(inFile,'w')

	fil.write(fileText)

	fil.close()

	pass


@python_2_unicode_compatible
class Bundle(models.Model):
    """
    Bundle has a many-one correspondance with User so a User can have multiple Bundles.
    Bundle name is currently not unique and we may want to ask someone whether or not it should be.
    If we require Bundle name to be unique, we could implement a get_or_create so multiple users
    can work on the same Bundle.  However we first must figure out how to click a Bundle and have it
    display the Build-A-Bundle app with form data pre-filled.  Not too sure how to go about this.
    """

    BUNDLE_STATUS = (
        ('b', 'Build'),
        ('r', 'Review'),
        ('s', 'Submit'),
    )
    BUNDLE_TYPE_CHOICES = (
        ('Archive', 'Archive'),
        ('Supplemental', 'Supplemental'),
    )

    bundle_type = models.CharField(max_length=12, choices=BUNDLE_TYPE_CHOICES, default='Archive',)
    name = models.CharField(max_length=MAX_CHAR_FIELD, unique=True)
    status = models.CharField(max_length=1, choices=BUNDLE_STATUS, blank=False, default='b')     
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE, default=get_most_current_version())


    # Accessors
    """
    - absolute_url
      Returns the url to continue the Build a Bundle process.
    """
    def absolute_url(self):
        return reverse('build:bundle', args=[str(self.id)])



    """
    """
    def directory(self):
        bundle_directory = os.path.join(settings.ARCHIVE_DIR, self.user.username)
        bundle_directory = os.path.join(bundle_directory, self.name_directory_case())
        return bundle_directory



    """
    - name_title_case
      Returns the bundle name in normal Title case with spaces.
    """
    def name_title_case(self):          
        name_edit = self.name
        name_edit = replace_all(name_edit, '_', ' ')
        return name_edit.title()



    """
    - name_directory_case
      Returns the bundle name in PDS4 compliant directory case with spaces.
      This is lid case with '_bundle' at the end.
    """
    def name_directory_case(self):

        # self.name is in title case with spaces
        name_edit = self.name

        # edit name to be in lower case        
        name_edit = name_edit.lower()

        # edit name to have underscores where spaces are present
        name_edit = replace_all(name_edit, ' ', '_')

        # edit name to append _bundle at the end
        name_edit = '{0}_bundle'.format(name_edit)

        return name_edit


    """
    """
    def name_file_case(self):

        # Get bundle name in directory case: {name_of_bundle}_bundle
        name_edit = self.name_directory_case()

        # Remove _bundle
        name_edit = name_edit[:-7]

        # Now we are returning {name_of_bundle} where {name_of_bundle} is lowercase with underscores rather than spaces
        return name_edit

    """
    name_lid_case
         - Returns the name in proper lid case.
             - Maximum Length: 255 characters
             - Allowed characters: lower case letters, digits, dash, period, underscore
             - Delimiters are colons (So no delimiters in name).
    """
    def name_lid_case(self):
        return self.name_file_case()

    def lid(self):
        return 'urn:{0}:{1}'.format(self.user.userprofile.agency, self.name_lid_case())



    # Constructors
    """ 
        build_directory currently is not working.
    """
    def build_directory(self):
        user_path = os.path.join(settings.ARCHIVE_DIR, self.user.username)
        print user_path
        bundle_path = os.path.join(user_path, self.name_directory_case())
        make_directory(bundle_path)
        self.save()
        


    # Meta
    def __str__(self):
        return self.name  

    class Meta:
        unique_together = ('user', 'name',)



    # Validators
    """
    validate_name
         - Returns the name in proper lid case.
             - Maximum Length: 255 characters
             - Allowed characters: lower case letters, digits, dash, period, underscore
             - Delimiters are colons (So no delimiters in name).
    """

@python_2_unicode_compatible
class Collections(models.Model):


    # Attributes
    bundle = models.OneToOneField(Bundle, on_delete=models.CASCADE)
    has_document = models.BooleanField(default=True)
    has_context = models.BooleanField(default=True)
    has_xml_schema = models.BooleanField(default=True)
    has_data = models.BooleanField(default=False)
    has_browse = models.BooleanField(default=False)
    has_calibrated = models.BooleanField(default=False)
    has_geometry = models.BooleanField(default=False)


    # Cleaners
    def list(self):
        collections_list = []
        if self.has_document:
            collections_list.append("document")
        if self.has_context:
            collections_list.append("context")
        if self.has_xml_schema:
            collections_list.append("xml_schema")
        if self.has_data:
            collections_list.append("data")
        if self.has_browse:
            collections_list.append("has_browse")
        if self.has_calibrated:
            collections_list.append("calibrated")
        if self.has_geometry:
            collections_list.append("has_geometry")
        return collections_list
        

    # Constructors
    def build_directories(self):
        for collection in self.list():
            collection_directory = os.path.join(self.bundle.directory(), collection)
            make_directory(collection_directory)


    # Meta
    #     Note: When we call on Collections, we want to be able to have a list of all collections 
    #           pertaining to a bundle.
    def __str__(self):
        return '{0} Bundle: document={1}, context={2}, xml_schema={3}, data={4}, browse={5}, calibrated={6}, geometry={7}'.format(self.bundle, self.has_document, self.has_context, self.has_xml_schema, self.has_data, self.has_browse, self.has_calibrated, self.has_geometry)
    class Meta:
        verbose_name_plural = 'Collections'





@python_2_unicode_compatible
class Data(models.Model):
    DATA_TYPE_CHOICES = (
        ('Calibrated', 'Calibrated'),
        ('Derived', 'Derived'),
        ('Raw', 'Raw'),
        ('Reduced', 'Reduced'),
    )
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=30, choices=DATA_TYPE_CHOICES, default='Archive',)


    # Meta
    def __str__(self):
        return 'Data associated'  # Better this once we work on data more

    class Meta:
        verbose_name_plural = 'Data'    







@python_2_unicode_compatible
class Product_Bundle(models.Model):
    bundle = models.OneToOneField(Bundle, on_delete=models.CASCADE)
    

    # Accessors

    def name_file_case(self):
        # Append bundle name in file case to name edit for a Product_Bundle xml label
        name_edit = 'bundle_{}.xml'.format(self.bundle.name_file_case())
        return name_edit

    
    """
        label gives the physical location of the label on atmos (or wherever).  Since Product_Bundle is located within the bundle directory, our path is .../user_directory_here/bundle_directory_here/product_bundle_label_here.xml.
    """
    def label(self):
        return os.path.join(self.bundle.directory(), self.name_file_case())


    # Builders
    """
        build_base_case copies the base case product_bundle template (versionless) into bundle dir
    """
    def build_base_case(self):

        
        # Locate base case Product_Bundle template found in templates/pds4_labels/base_case/product_bundle
        source_file = os.path.join(settings.TEMPLATE_DIR, 'pds4_labels')
        source_file = os.path.join(source_file, 'base_case')
        source_file = os.path.join(source_file, 'product_bundle.xml')

	#set selected version
	update = Version()
	bundle = Bundle()
	update.version_update(bundle.version, source_file)

        # Copy the base case template to the correct directory
        copyfile(source_file, self.label())
        
        return
        

    # Cleaners


    # Fillers
    """
        fill_base_case is the initial fill given the bundle name, version, and collections.
    """
    def fill_base_case(self, root):
        Product_Bundle = root
         
        # Fill in Identification_Area
        Identification_Area = Product_Bundle.find('{}Identification_Area'.format(NAMESPACE))

        #     lid
        logical_identifier = Identification_Area.find('{}logical_identifier'.format(NAMESPACE))
        logical_identifier.text = self.bundle.lid()
        

        #     version_id --> Note:  Can be changed to be more dynamic once we implement bundle versions (which is different from PDS4 versions)
        version_id = Identification_Area.find('{}version_id'.format(NAMESPACE))
        version_id.text = '1.0'  

        #     title
        title = Identification_Area.find('{}title'.format(NAMESPACE))
        title.text = self.bundle.name_title_case()

        #     information_model_version
        #information_model_version = Identification_Area.find('{}information_model_version'.format(NAMESPACE))
        #information_model_version = self.bundle.version.name_with_dots()
        
        return Product_Bundle

    """
        build_internal_reference builds and fills the Internal_Reference information within the Reference_List of Product_Bundle.  The relation is used within reference_type to associate what the bundle is related to, like bundle_to_document.  Therefore, relation is a model object in ELSA, like Document.  The possible relations as of V1A00 are errata, document, investigation, instrument, instrument_host, target, resource, associate.
    """

    def build_internal_reference(self, root, relation):

        Reference_List = root.find('{}Reference_List'.format(NAMESPACE))

        Internal_Reference = etree.SubElement(Reference_List, 'Internal_Reference')

        lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
        lid_reference.text = relation.lid()

        reference_type = etree.SubElement(Internal_Reference, 'reference_type')
        reference_type.text = 'bundle_to_{}'.format(relation.reference_type())   

        return root   

    # Meta
    def __str__(self):
        return '{}: Product Bundle'.format(self.bundle)

    # Label Constructors
    def base_case(self):
        return

    # Validators






@python_2_unicode_compatible
class Product_Collection(models.Model):
    COLLECTION_CHOICES = (

        ('Document','Document'),
        ('Context','Context'),
        ('XML_Schema','XML_Schema'),
        ('Data','Data'),
        ('Browse','Browse'),
        ('Geometry','Geometry'),
        ('Calibration','Calibration'),
        ('Not_Set','Not_Set'),

    )
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    collection = models.CharField(max_length=MAX_CHAR_FIELD, choices=COLLECTION_CHOICES, default='Not_Set')
    


    # Accessors
    def directory(self):
        name_edit = self.collection.lower()
        collection_directory = os.path.join(self.bundle.directory(), name_edit)
        return collection_directory



    """
       name_label_case returns the name in label case with the proper .xml extension.
    """        
    def name_label_case(self):

        # Append cleaned bundle name to name edit for Product_Bundle xml label
        name_edit = self.collection.lower()
        name_edit = 'collection_{}.xml'.format(name_edit)
        return name_edit


    """
       label returns the physical label location in ELSAs archive
    """
    def label(self):
        return os.path.join(self.directory(), self.name_label_case())


    # Cleaners

    # Label Constructors
    def build_base_case(self):
        
        # Locate base case Product_Collection template found in templates/pds4_labels/base_case/
        source_file = os.path.join(PDS4_LABEL_TEMPLATE_DIRECTORY, 'base_case')
        source_file = os.path.join(source_file, 'product_collection.xml')

        # Locate collection directory and create path for new label
        label_file = os.path.join(self.directory(), self.name_label_case())

	#set selected version
	#set selected version
	update = Version()
	bundle = Bundle()
	update.version_update(bundle.version, source_file)

        # Copy the base case template to the correct directory
        copyfile(source_file, label_file)
            
        return


    # Fillers
    def fill_base_case(self, root):
        Product_Collection = root
         
        # Fill in Identification_Area
        Identification_Area = Product_Collection.find('{}Identification_Area'.format(NAMESPACE))

        #     lid
        logical_identifier = Identification_Area.find('{}logical_identifier'.format(NAMESPACE))
        logical_identifier.text = 'urn:{0}:{1}:{2}'.format(self.bundle.user.userprofile.agency, self.bundle.name_lid_case(), self.collection) # where agency is something like nasa:pds
        

        #     version_id --> Note:  Can be changed to be more dynamic once we implement bundle versions (which is different from PDS4 versions)
        version_id = Identification_Area.find('{}version_id'.format(NAMESPACE))
        version_id.text = '1.0'  

        #     title
        title = Identification_Area.find('{}title'.format(NAMESPACE))
        title.text = self.bundle.name_title_case()

        #     information_model_version
        #information_model_version = Identification_Area.find('{}information_model_version'.format(NAMESPACE))
        #information_model_version = self.bundle.version.name_with_dots()
        
        return Product_Collection

    """
        build_internal_reference builds and fills the Internal_Reference information within the Reference_List of Product_Collection.  The relation is used within reference_type to associate what the collection is related to, like collection_to_document.  Therefore, relation is a model object in ELSA, like Document.  The possible relations as of V1A00 are resource, associate, calibration, geometry, spice kernel, document, browse, context, data, ancillary, schema, errata, bundle, personnel, investigation, instrument, instrument_host, target.
    """

    def build_internal_reference(self, root, relation):

        Reference_List = root.find('{}Reference_List'.format(NAMESPACE))

        Internal_Reference = etree.SubElement(Reference_List, 'Internal_Reference')

        lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
        lid_reference.text = relation.lid()

        reference_type = etree.SubElement(Internal_Reference, 'reference_type')
        reference_type.text = 'collection_to_{}'.format(relation.reference_type())   

        return root   

    # Meta
    def __str__(self):
        
        return "{0}: Product Collection for {1} Collection".format(self.bundle, self.collection)


    # Validators



"""
12.1  Document

Root Class:Tagged_NonDigital_Object
Role:Concrete

Class Description:The Document class describes a document.

Steward:pds
Namespace Id:pds
Version Id:2.0.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Tagged_NonDigital_Object	 	 	 
        	. TNDO_Supplemental	 	 	 
 	        . . Document	 	 	 

Subclass	none	 	 	 

Attribute
	acknowledgement_text	0..1	 	 
 	author_list     	0..1	 	 
 	copyright       	0..1	 	 
 	description	        0..1	 	 
 	document_editions	0..1	 	 
 	document_name	        0..1  An exec decision has been made to make document_name required 
 	doi	                0..1	 	 
 	editor_list	        0..1	 	 
 	publication_date	1	 	 
 	revision_id	        0..1	 	 

Inherited Attribute	none	 	 	 
Association	        data_object	        1	Digital_Object	 
 	                has_document_edition	1..*	Document_Edition	 
Inherited Association	none	 	 	 
Referenced from	Product_Document	 	 	 
"""
@python_2_unicode_compatible
class Product_Document(models.Model):

    # Attributes
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    acknowledgement_text = models.CharField(max_length=MAX_CHAR_FIELD)
    author_list = models.CharField(max_length=MAX_CHAR_FIELD)
    copyright = models.CharField(max_length=MAX_CHAR_FIELD)
    description = models.CharField(max_length=MAX_CHAR_FIELD)
    document_editions = models.CharField(max_length=MAX_CHAR_FIELD)
    document_name = models.CharField(max_length=MAX_CHAR_FIELD)
    doi = models.CharField(max_length=MAX_CHAR_FIELD)
    editor_list = models.CharField(max_length=MAX_CHAR_FIELD)
    publication_date = models.CharField(max_length=MAX_CHAR_FIELD)
    revision_id = models.CharField(max_length=MAX_CHAR_FIELD)


    # Accessors
    def collection(self):
        return 'document'

    def directory(self):
        """
            Documents are found in the Document collection
        """
        collection_directory = os.path.join(self.bundle.directory(), 'document')
        return collection_directory

    def name_label_case(self):
        """
            This could be improved to ensure disallowed characters for a file name are not contained
            in name.
        """
        name_edit = self.document_name.lower()
        name_edit = replace_all(name_edit, ' ', '_')
        return name_edit


    def label(self):
        """
            label returns the physical label location in ELSAs archive
        """
        return os.path.join(self.directory(), self.name_label_case())

    def lid(self):
        return '{0}:document:{1}'.format(self.bundle.lid(), self.name_label_case())

    def reference_type(self):
        return 'document'





    # Builders
    def build_base_case(self):
        
        # Locate base case Product_Document template found in templates/pds4_labels/base_case/
        source_file = os.path.join(PDS4_LABEL_TEMPLATE_DIRECTORY, 'base_case')
        source_file = os.path.join(source_file, 'product_document.xml')

        # Locate collection directory and create path for new label
        label_file = os.path.join(self.directory(), self.name_label_case())

	#set selected version
	update = Version()
	bundle = Bundle()
	update.version_update(bundle.version, source_file)

        # Copy the base case template to the correct directory
        copyfile(source_file, label_file)
            
        return


    def fill_base_case(self, root):

        Product_Document = root

        # Fill in Identification_Area
        Identification_Area = Product_Document.find('{}Identification_Area'.format(NAMESPACE))

        logical_identifier = Identification_Area.find('{}logical_identifier'.format(NAMESPACE))
        logical_identifier.text =  'urn:{0}:{1}:{2}:{3}'.format(self.bundle.user.userprofile.agency, self.bundle.name_lid_case(), 'document', self.document_name) # where agency is something like nasa:pds

        version_id = Identification_Area.find('{}version_id'.format(NAMESPACE))
        version_id.text = '1.0'  # Can make this better

        title = Identification_Area.find('{}title'.format(NAMESPACE))
        title.text = self.document_name

        information_model_version = Identification_Area.find('information_model_version')
        #information_model_version.text = self.bundle.version.with_dots()   
        
        
        # Fill in Document
        Document = Product_Document.find('{}Document'.format(NAMESPACE))
        if self.revision_id:
            revision_id = etree.SubElement(Document, 'revision_id')
            revision_id.text = self.revision_id
        if self.document_name:
            document_name = etree.SubElement(Document, 'document_name')
            document_name.text = self.document_name
        if self.doi:
            doi = etree.SubElement(Document, 'doi')
            doi.text = self.doi
        if self.author_list:
            author_list = etree.SubElement(Document, 'author_list')
            author_list.text = self.author_list
        if self.editor_list:
            editor_list = etree.SubElement(Document, 'editor_list')
            editor_list.text = self.editor_list
        if self.acknowledgement_text:
            acknowledgement_text = etree.SubElement(Document, 'acknowledgement_text')
            acknowledgement_text.text = self.acknowledgement_text
        if self.copyright:
            copyright = etree.SubElement(Document, 'copyright')
            copyright.text = self.author_list
        if self.publication_date:  # this should always be true 
            publication_date = etree.SubElement(Document, 'publication_date')
            publication_date.text = self.publication_date
        if self.document_editions:
            document_editions = etree.SubElement(Document, 'document_editions')
            document_editions.text = self.document_editions   
        if self.description:
            description = etree.SubElement(Document, 'description')
            description.text = self.description     

        return root        


    def build_internal_reference(self, root, relation):
        """
            build_internal_reference needs to be completed
        """
        pass     

    # Meta
    def __str__(self):
        return 'Need to finish this.'


   





"""
10.1  Alias

Root Class:Product_Components
Role:Concrete

Class Description:The Alias class provides a single alternate name and identification for this product in this or some other archive or data system.

Steward:pds
Namespace Id:pds
Version Id:1.0.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Product_Components	 	 	 
 	. Alias	 	 	 

Subclass	none	 	 	 

Attribute	alternate_id	0..1	 	 
        	alternate_title	0..1	 	 
        	comment	        0..1	 	 

Inherited Attribute	none	 	 	 
Association	        none	 	 	 
Inherited Association	none	 	 	 

Referenced from	Alias_List	 	 	 
"""
@python_2_unicode_compatible
class Alias(models.Model):

    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    alternate_id = models.CharField(max_length=MAX_CHAR_FIELD)
    alternate_title = models.CharField(max_length=MAX_CHAR_FIELD)
    comment = models.CharField(max_length=MAX_CHAR_FIELD)
    
    # Builders
    def build_alias(self, label_root):
        
         
        # Find Identification_Area
        Identification_Area = label_root.find('{}Identification_Area'.format(NAMESPACE))

        # Find Alias_List.  If no Alias_List is found, make one.
        Alias_List = Identification_Area.find('{}Alias_List'.format(NAMESPACE))
        if Alias_List is None:
            Alias_List = etree.SubElement(Identification_Area, 'Alias_List')

        # Add Alias information
        Alias = etree.SubElement(Alias_List, 'Alias')
        if self.alternate_id:
            alternate_id = etree.SubElement(Alias, 'alternate_id')
            alternate_id.text = self.alternate_id
        if self.alternate_title:
            alternate_title = etree.SubElement(Alias, 'alternate_title')
            alternate_title.text = self.alternate_title
        if self.comment:
            comment = etree.SubElement(Alias, 'comment')
            comment.text = self.comment
        
        
        return label_root

    # Meta
    def __str__(self):
        return 'Need to finish this.'

    # Admin Stuff
    class Meta:
        verbose_name_plural = 'Aliases'

"""
10.3  Citation_Information

Root Class:Product_Components
Role:Concrete

Class Description:The Citation_Information class provides specific fields often used in citing the product in journal articles, abstract services, and other reference contexts.

Steward:pds
Namespace Id:pds
Version Id:1.2.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Product_Components	 	 	 
         	. Citation_Information	 	 	 

Subclass	none	 
	 	 
Attribute	author_list     	0..1	 	 
        	description      	1	 	 
        	editor_list      	0..1	 	 
        	keyword	                0..*	 	 
 	        publication_year	1	
 	 
Inherited Attribute	none	 	 	 
Association	        none	 	 	 
Inherited Association	none	 	 	 

Referenced from	Identification_Area	
""" 	 	 
@python_2_unicode_compatible
class Citation_Information(models.Model):

    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    author_list = models.CharField(max_length=MAX_CHAR_FIELD)
    description = models.CharField(max_length=MAX_CHAR_FIELD)
    editor_list = models.CharField(max_length=MAX_CHAR_FIELD)
    keyword = models.CharField(max_length=MAX_CHAR_FIELD)
    publication_year = models.CharField(max_length=MAX_CHAR_FIELD)
    
    # Builders
    def build_citation_information(self, label_root):
        
         
        # Find Identification_Area
        Identification_Area = label_root.find('{}Identification_Area'.format(NAMESPACE))

        # Find Alias_List.  If no Alias_List is found, make one.
        Citation_Information = Identification_Area.find('{}Citation_Information'.format(NAMESPACE))

        # Double check but I'm pretty sure Citation_Information is only added once.  
        #if Citation_Information is None:
        Citation_Information = etree.SubElement(Identification_Area, 'Citation_Information')

        # Add Citation_Information information
        if self.author_list:
            author_list = etree.SubElement(Citation_Information, 'author_list')
            author_list.text = self.author_list
        if self.editor_list:
            editor_list = etree.SubElement(Citation_Information, 'editor_list')        
            editor_list.text = self.editor_list
        if self.keyword:
            keyword = etree.SubElement(Citation_Information, 'keyword')  # Ask how keywords are saved #
            keyword.text = self.keyword
        publication_year = etree.SubElement(Citation_Information, 'publication_year')
        publication_year.text = self.publication_year
        description = etree.SubElement(Citation_Information, 'description')
        description.text = self.description
        return label_root

    # Meta
    def __str__(self):
        return 'Need to finish this.'

"""
"""
#class I

    # Admin Stuff







#    To Be Garbage Here✲






