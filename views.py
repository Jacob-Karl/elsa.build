# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render






#    Create your views here  
@login_required
def alias(request, pk_bundle):
    print '-------------------------------------------------------------------------'
    print '\n\n-------------------- Add an Alias with ELSA -------------------------'
    print '------------------------------ DEBUGGER ---------------------------------'

    # Get forms
    form_alias = AliasForm(request.POST or None)
    bundle = Bundle.objects.get(pk=pk_bundle)

    # Declare context_dict for template
    context_dict = {
        'form_alias':form_alias,
        'bundle':bundle,

    }

    # After ELSAs friend hits submit, if the forms are completed correctly, we should enter
    # this conditional.
    print '\n\n------------------------------- ALIAS INFO --------------------------------'
    if form_alias.is_valid():
        print 'form_alias is valid'
        # Create Alias model object
        alias = form_alias.save(commit=False)
        alias.bundle = bundle
        alias.save()
        print 'Alias model object: {}'.format(alias)

        # Find appropriate label(s).  Alias gets added to all labels in a Bundle.
        all_labels = []
        product_bundle = Product_Bundle.objects.get(bundle=bundle)
        product_collections_list = Product_Collection.objects.filter(bundle=bundle)
        all_labels.append(product_bundle)
        all_labels.extend(product_collections_list)

        for label in all_labels:

            # Open appropriate label(s).  
            print '- Label: {}'.format(label)
            print ' ... Opening Label ... '
            label_list = open_label(label.label())
            label_object = label_list[0]
            label_root = label_list[1]
        
            # Build Alias
            print ' ... Building Label ... '
            label_root = alias.build_alias(label_root)

            # Close appropriate label(s)
            print ' ... Closing Label ... '
            close_label(label_object, label_root)

            print '---------------- End Build Alias -----------------------------------'        
        return render(request, 'build/alias/alias.html', context_dict)
    return render(request, 'build/alias/alias.html',context_dict)

@login_required
def build(request): 
    print '-------------------------------------------------------------------------'
    print '\n\n---------------- Welcome to Build A Bundle with ELSA --------------------'
    print '------------------------------ DEBUGGER ---------------------------------'


    # Get forms
    form_bundle = BundleForm(request.POST or None)
    form_collections = CollectionsForm(request.POST or None)

    # Declare context_dict for template
    context_dict = {
        'form_bundle':form_bundle,
        'form_collections':form_collections,
        'user':request.user,
    }

    print '\n\n------------------------------- USER INFO -------------------------------'
    print 'User:    {}'.format(request.user)
    print 'Agency:  {}'.format(request.user.userprofile.agency)


    print '\n\n------------------------------- BUILD INFO --------------------------------'
    # After ELSAs friend hits submit, if the forms are completed correctly, we should enter here
    # this conditional.
    if form_bundle.is_valid() and form_collections.is_valid():
        print 'form_bundle and form_collections are valid'

        # Check Uniqueness  --- GOTTA BE A BETTER WAY (k)
        bundle_name = form_bundle.cleaned_data['name']
        bundle_user = request.user
        bundle_count = Bundle.objects.filter(name=bundle_name, user=bundle_user).count()
        # If user and bundle name are unique, then...
        if bundle_count == 0:

            # Create Bundle model.
            bundle = form_bundle.save(commit=False)
            bundle.user = request.user
            bundle.status = 'b' # b for build.  New Bundles are always in build stage first.
            bundle.save()
            print 'Bundle model object: {}'.format(bundle)

            # Build PDS4 Ccmpliant Bundle directory in User Directory.
            bundle.build_directory()
            print 'Bundle directory: {}'.format(bundle.directory())

            # Create Product_Bundle model.
            product_bundle = ProductBundleForm().save(commit=False)
            product_bundle.bundle = bundle
            product_bundle.save()
            print 'product_bundle model object: {}'.format(product_bundle)

            # Build Product_Bundle label using the base case template found in
            # templates/pds4/basecase
            print '\n---------------Start Build Product_Bundle Base Case------------------------'
            product_bundle.build_base_case()  # simply copies baseecase to user bundle directory
            # Open label - returns a list where index 0 is the label object and 1 is the tree
            print ' ... Opening Label ... '
            label_list = open_label(product_bundle.label()) #list = [label_object, label_root]
            label_object = label_list[0]
            label_root = label_list[1]
            # Fill label - fills 
            print ' ... Filling Label ... '
            label_root = product_bundle.fill_base_case(label_root)
            # Close label
            print ' ... Closing Label ... '
            close_label(label_object, label_root)           
            print '---------------- End Build Product_Bundle Base Case -------------------------'
  
            # Create Collections Model Object and list of Collections, list of Collectables
            collections = form_collections.save(commit=False)
            collections.bundle = bundle
            collections.save()
            print '\nCollections model object:    {}'.format(collections)
            
            # Create PDS4 compliant directories for each collection within the bundle.            
            collections.build_directories()

            # Each collection in collections needs a model and a label
            for collection in collections.list():

                # Create Product_Collection model for each collection
                product_collection = ProductCollectionForm().save(commit=False)
                product_collection.bundle = bundle
                if collection == 'document':
                    product_collection.collection = 'Document'
                elif collection == 'context':
                    product_collection.collection = 'Context'
                elif collection == 'xml_schema':
                    product_collection.collection = 'XML_Schema'
                elif collection == 'data':
                    product_collection.collection = 'Data'
                elif collection == 'browse':
                    product_collection.collection = 'Browse'
                elif collection == 'geometry':
                    product_collection.collection = 'Geometry'
                elif collection == 'calibration':
                    product_collection.collection = 'Calibration'
                product_collection.save()
                print '\n\n{} Collection Directory:    {}'.format(collection, product_collection.directory())

                # Build Product_Collection label
                print '-------------Start Build Product_Collection Base Case-----------------'
                product_collection.build_base_case()

                # Open Product_Collection label
                print ' ... Opening Label ... '
                label_list = open_label(product_collection.label())
                label_object = label_list[0]
                label_root = label_list[1]

                # Fill label
                print ' ... Filling Label ... '
                label_root = product_collection.fill_base_case(label_root)

                # Close label
                print ' ... Closing Label ... '
                close_label(label_object, label_root)
                print '-------------End Build Product_Collection Base Case-----------------'
           
            # Further develop context_dict entries for templates            
            context_dict['Bundle'] = bundle
            context_dict['Product_Bundle'] = Product_Bundle.objects.get(bundle=bundle)
            context_dict['Product_Collection_Set'] = Product_Collection.objects.filter(bundle=bundle)

            return render(request, 'build/two.html', context_dict)

    return render(request, 'build/build.html', context_dict)

# The bundle_detail view is the page that details a specific bundle.
@login_required
def bundle(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)
    bundle_user = bundle.user


    print 'BEGIN bundle_detail VIEW'
    if request.user == bundle.user:
        context_dict = {
            'bundle':bundle,
            'collections': Collections.objects.get(bundle=bundle),
        }
        return render(request, 'build/bundle/bundle.html', context_dict)

    else:
        return redirect('main:restricted_access')

# The bundle_download view is not a page.  When a user chooses to download a bundle, this 'view' manifests and begins the downloading process.
def bundle_download(request, pk_bundle):
    # Grab bundle directory
    bundle = Bundle.objects.get(pk=pk_bundle)

    print 'BEGIN bundle_download VIEW'
    print 'Username: {}'.format(request.user.username)
    print 'Bundle directory name: {}'.format(bundle.get_name_directory())
    print 'Current working directory: {}'.format(os.getcwd())
    print settings.TEMPORARY_DIR
    print settings.ARCHIVE_DIR

    # Make tarfile
    #    Note: This does not run in build directory, it runs in elsa directory.  
    #          Uncomment print os.getcwd() if you need the directory to see for yourself.
    tar_bundle_dir = '{}.tar.gz'.format(bundle.get_name_directory())
    temp_dir = os.path.join(settings.TEMPORARY_DIR, tar_bundle_dir)
    source_dir = os.path.join(settings.ARCHIVE_DIR, request.user.username)
    source_dir = os.path.join(source_dir, bundle.get_name_directory())
    make_tarfile(temp_dir, source_dir)

    # Testing.  See if simply bundle directory will download.
    # Once finished, make directory a tarfile and then download.
    file_path = os.path.join(settings.TEMPORARY_DIR, tar_bundle_dir)


    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-tar")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    return HttpResponse("Download did not work.")

# The bundle_delete view is the page a user sees once they select the delete bundle button.  This view gives the user an option to confirm or take back their choice.  This view could be improved upon.
@login_required
def bundle_delete(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)
    user = bundle.user
    delete_bundle_form = ConfirmForm(request.POST or None)

    context_dict = {}
    context_dict['bundle'] = bundle
    context_dict['user'] = user
    context_dict['delete_bundle_form'] = delete_bundle_form
    context_dict['decision'] = 'has yet to have the chance to be'

    # Secure:  If current user is the user associated with the bundle, then...
    if request.user == user:
        if delete_bundle_form.is_valid():
            print 'delete_bundle_form is valid'
            print 'decision: {}'.format(delete_bundle_form.cleaned_data["decision"])
            decision = delete_bundle_form.cleaned_data['decision']
            if decision == 'Yes':
                context_dict['decision'] = 'was'
                success_status = remove.bundle_dir_and_model(bundle, user)
                if success_status:
                    return redirect('../../success_delete/')


            if decision == 'No':
                # Go back to bundle page
                context_dict['decision'] = 'was not'

        return render(request, 'build/bundle/confirm_delete.html', context_dict)

    # Secure: Current user is not the user associated with the bundle, so...
    else:
        return redirect('main:restricted_access')

def citation_information(request, pk_bundle):
    print '-------------------------------------------------------------------------'
    print '\n\n--------------- Add Citation_Information with ELSA -------------------'
    print '------------------------------ DEBUGGER ---------------------------------'

    # Get forms
    form_citation_information = CitationInformationForm(request.POST or None)
    bundle = Bundle.objects.get(pk=pk_bundle)

    # Declare context_dict for template
    context_dict = {
        'form_citation_information':form_citation_information,
        'bundle':bundle,

    }

    # After ELSAs friend hits submit, if the forms are completed correctly, we should enter
    # this conditional.
    print '\n\n----------------- CITATION_INFORMATION INFO -------------------------'
    if form_citation_information.is_valid():
        print 'form_citation_information is valid'
        # Create Citation_Information model object
        citation_information = form_citation_information.save(commit=False)
        citation_information.bundle = bundle
        citation_information.save()
        print 'Citation Information model object: {}'.format(citation_information)

        # Find appropriate label(s).  Alias gets added to all labels in a Bundle.
        all_labels = []
        product_bundle = Product_Bundle.objects.get(bundle=bundle)
        product_collections_list = Product_Collection.objects.filter(bundle=bundle)
        all_labels.append(product_bundle)             # Append because a single item
        all_labels.extend(product_collections_list)   # Extend because a list

        for label in all_labels:

            # Open appropriate label(s).  
            print '- Label: {}'.format(label)
            print ' ... Opening Label ... '
            label_list = open_label(label.label())
            label_object = label_list[0]
            label_root = label_list[1]
        
            # Build Citation Information
            print ' ... Building Label ... '
            label_root = citation_information.build_citation_information(label_root)

            # Close appropriate label(s)
            print ' ... Closing Label ... '
            close_label(label_object, label_root)

            print '------------- End Build Citation Information -------------------'        
        return render(request, 'build/citation_information/citation_information.html', context_dict)
    return render(request, 'build/citation_information/citation_information.html',context_dict)


@login_required
def data(request, pk_bundle): 
    print '-------------------------------------------------------------------------'
    print '\n\n---------------------- Add Data with ELSA ---------------------------'
    print '------------------------------ DEBUGGER ---------------------------------'

    # Get bundle
    bundle = Bundle.objects.get(pk=pk_bundle)

    # Get forms
    form_data = DataForm(request.POST or None)
    form_product_observational = ProductObservationalForm(request.POST or None)

    # Context Dictionary
    context_dict = {
        'bundle':bundle,
        'form_data':form_data,
        'form_product_observational':form_product_observational,
    }
    # After ELSAs friend hits submit, if the forms are completed correctly, we should enter
    # this conditional.
    print '\n\n------------------------ DATA INFO ----------------------------------'
    if form_data.is_valid() and form_product_observational.is_valid():

        # Create Data model object
        data = form_data.save(commit=False)
        data.bundle = bundle
        data.save()
        print 'Data model object: {}'.format(data)

        # Create Product_Observational model object
        product_observational = form_product_observational.save(commit=False)
        product_observational.bundle = bundle
        product_observational.data = data
        product_observational.processing_level = data.data_type
        product_observational.save()
        print 'Product_Observational model object: {}'.format(product_observational)

        # Create Data Folder corresponding to processing level
        data.build_directory()

        print '---------------- End Build Product_Observational Base Case -------------------------'
                # Copy Product_Observational label
        product_observational.build_base_case()

        # Open label - returns a list of label information where list = [label_object, label_root]
        print ' ... Opening Label ... '
        label_list = open_label(product_observational.label())
        label_object = label_list[0]
        label_root = label_list[1]
        # Fill label - fills 
        print ' ... Filling Label ... '
        label_root = product_observational.fill_base_case(label_root)
        # Close label
        print ' ... Closing Label ... '
        close_label(label_object, label_root)           
        print '---------------- End Build Product_Observational Base Case -------------------------'

        # Update context_dict
        print '\n\n---------------------- UPDATING CONTEXT DICTIONARY -----------------------------'
        context_dict['data'] = data
        context_dict['product_observational'] = product_observational  # Needs a fix
        
    data_set = Data.objects.filter(bundle=bundle)
    context_dict['data_set'] = data_set
    product_observational_set = []
    for data in data_set:
        product_observational_set.extend(Product_Observational.objects.filter(data=data))
    context_dict['product_observational_set'] = product_observational_set
      
    return render(request, 'build/data/data.html', context_dict)

def document(request, pk_bundle):
    print '-------------------------------------------------------------------------'
    print '\n\n--------------------- Add Document with ELSA ------------------------'
    print '------------------------------ DEBUGGER ---------------------------------'

    # Get forms
    form_product_document = ProductDocumentForm(request.POST or None)
    bundle = Bundle.objects.get(pk=pk_bundle)

    # Declare context_dict for template
    context_dict = {
        'form_product_document':form_product_document,
        'bundle':bundle,

    }

    # After ELSAs friend hits submit, if the forms are completed correctly, we should enter
    # this conditional.  We must do [] things: 1. Create the Document model object, 2. Add a Product_Document label to the Document Collection, 3. Add the Document as an Internal_Reference to the proper labels (like Product_Bundle and Product_Collection).
    print '\n\n---------------------- DOCUMENT INFO -------------------------------'
    if form_product_document.is_valid():
        print 'form_product_document is valid'  

        # Create Document Model Object
        product_document = form_product_document.save(commit=False)
        product_document.bundle = bundle
        product_document.save()
        print 'Product_Document model object: {}'.format(product_document)

        # Build Product_Document label using the base case template found in templates/pds4/basecase
        print '\n---------------Start Build Product_Document Base Case------------------------'
        product_document.build_base_case()
        # Open label - returns a list where index 0 is the label object and 1 is the tree
        print ' ... Opening Label ... '
        label_list = open_label(product_document.label())
        label_object = label_list[0]
        label_root = label_list[1]
        # Fill label - fills 
        print ' ... Filling Label ... '
        label_root = product_document.fill_base_case(label_root)
        # Close label
        print ' ... Closing Label ... '
        close_label(label_object, label_root)           
        print '---------------- End Build Product_Document Base Case -------------------------' 

        # Add Document info to proper labels.  For now, I simply have Product_Bundle and Product_Collection.  This list will need to be updated.
        print '\n---------------Start Build Internal_Reference for Document-------------------'
        all_labels = []
        product_bundle = Product_Bundle.objects.get(bundle=bundle)
        product_collections_list = Product_Collection.objects.filter(bundle=bundle)

        all_labels.append(product_bundle)
        all_labels.extend(product_collections_list)  

        for label in all_labels:
            print '- Label: {}'.format(label)
            print ' ... Opening Label ... '
            label_list = open_label(label.label())
            label_object = label_list[0]
            label_root = label_list[1]
        
            # Build Internal_Reference
            print ' ... Building Internal_Reference ... '
            label_root = label.build_internal_reference(label_root, product_document)

            # Close appropriate label(s)
            print ' ... Closing Label ... '
            close_label(label_object, label_root)
        print '\n----------------End Build Internal_Reference for Document-------------------'
        
    return render(request, 'build/document/document.html',context_dict)



 
def product_observational(request, pk_bundle, pk_product_observational):

    print '-------------------------------------------------------------------------'
    print '\n\n---------------- Add Product_Observational with ELSA ----------------'
    print '------------------------------ DEBUGGER ---------------------------------'

    bundle = Bundle.objects.get(pk=pk_bundle)
    product_observational = Product_Observational.objects.get(pk=pk_product_observational)
    form_product_observational = TableForm(request.POST or None)
    context_dict = {
        'bundle':bundle,
        'product_observational':product_observational,
        'form_product_observational':form_product_observational,

    }

    print '\n\n----------------- PRODUCT_DOCUMENT INFO -----------------------------'
    if form_product_observational.is_valid():
        print 'form_product_observational is valid.'
        # Create the associated model (Table, Array, Cube, etc...)
        observational = form_product_observational.save(commit=False)
        observational.product_observational = product_observational
        observational.save()
        print 'observational object: {}'.format(observational)
        

        print '\n--------- Start Add Observational to Product_Observational -----------------'
        # Open label
        print ' ... Opening Label ... '
        label_list = open_label(product_observational.label())
        label_object = label_list[0]
        label_root = label_list[1]
        print label_root

        # Fill label
        print ' ... Filling Label ... '
        label_root = product_observational.fill_observational(label_root, observational)

        # Close label
        print ' ... Closing Label ... '
        close_label(label_object, label_root)
        print '-------------End Add Observational to Product_Observational -----------------'
        
    # Now we must grab the observational set to display on ELSA's template for the Product_Observational page.  Right now, this is tables so it is easy.
        observational_set = Table.objects.filter(product_observational=product_observational)
    
    return render(request, 'build/data/table.html', context_dict)
