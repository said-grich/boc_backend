from datetime import datetime
from .models import ExtractedData  # Import your Django model
from .excel_controller import *
from .pdf_controller import *
from .github_controller import *
import uuid
def process_uploaded_file(file_path, uploaded_file_name, tag_names, user):
    results_by_tag_exact = {tag: [] for tag in tag_names}
    results_by_tag_partial = {tag: [] for tag in tag_names}
    file_type=None
    if uploaded_file_name.endswith('.pdf'):
        file_type="PDF"
        # Process PDF files
        text_data = read_pdf_file(file_path)
        for tag in tag_names:
            result_exact, result_partial = search_pdf(text_data, tag, uploaded_file_name, "PDF", user)
            results_by_tag_exact[tag] += result_exact
            results_by_tag_partial[tag] += result_partial

    elif uploaded_file_name.endswith('.docx'):
        file_type="Word"
        text_data = read_doc_file(file_path)
        for tag in tag_names:
            result_exact, result_partial = search_pdf(text_data, tag, uploaded_file_name, "Word", user)
            results_by_tag_exact[tag] += result_exact
            results_by_tag_partial[tag] += result_partial

    elif uploaded_file_name.endswith('.xls') or uploaded_file_name.endswith('.xlsx'):
        file_type="Excel"
        for tag in tag_names:
            result_exact, result_partial = extract_text_from_excel(file_path, tag, uploaded_file_name, user)
            results_by_tag_exact[tag] += result_exact
            results_by_tag_partial[tag] += result_partial

    elif uploaded_file_name.endswith('.zip'):
        file_type="Github"
        zip_file_name = uploaded_file_name.split(".")[0]
        data_dict = read_all_files_in_directory(file_path)
        for tag in tag_names:
            result_exact, result_partial = search_github(tag, zip_file_name, data_dict)
            results_by_tag_exact[tag] += result_exact
            results_by_tag_partial[tag] += result_partial

    else:
        raise ValueError(f"Unsupported file format: {uploaded_file_name}")

    return file_type, results_by_tag_exact, results_by_tag_partial



def save_results_to_db(results, file_name, file_type, match_type, user):

    search_id = uuid.uuid4()
    print("UUID",search_id)

    saved_results = []

    for tag, result_list in results.items():
        for result in result_list:
            saved_result = ExtractedData.objects.create(
                search_id=search_id,  # Assign the generated search ID
                source_file_name=file_name,
                file_type=file_type,
                tag_searched=tag,
                block_record=result['Block/Record'],
                location_of_tag=result['Location of the Tag'],
                # date_of_search is automatically set with auto_now_add=True
                search_author=user,
                match_type=match_type,
                other=result.get('Other', ''),
                # line_id will be automatically generated in the save method if not provided
            )
            # Append the saved instance to the list
            saved_results.append(saved_result)

    return saved_results



def find_records(source_file_name=None, file_type=None, tag_searched=None, start_date=None, end_date=None, search_author=None):

    records = ExtractedData.objects.all()

    # Apply filters based on provided arguments
    if source_file_name:
        records = records.filter(source_file_name__icontains=source_file_name)

    if file_type:
        records = records.filter(file_type__iexact=file_type)

    if tag_searched:
        records = records.filter(tag_searched__icontains=tag_searched)

    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        records = records.filter(date_of_search__gte=start_date_obj)

    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        records = records.filter(date_of_search__lte=end_date_obj)

    if search_author:
        records = records.filter(search_author__icontains=search_author)

    return records
