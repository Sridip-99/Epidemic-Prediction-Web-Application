import os
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from .prediction import process_and_predict
from django.contrib import messages


# ======================================
# 1. Tool View for 'specialuser' Group
# ======================================
# Ensure the user belongs to 'specialuser' group before accessing the tool
@login_required(login_url='login')  # Redirect to login if not authenticated
@permission_required('tool_app.access_tool', raise_exception=True)  # Custom permission for tool access
def tool_view(request):
    return render(request, "tool_app/tool.html", {'title': 'Prediction-Tool'})


# ===================================================================
# 2. Result View for 'specialuser' Group only after uploading dataset
# ===================================================================
# Handle file upload and process predictions
@login_required(login_url='login')  # Redirect to login if not authenticated
@permission_required('tool_app.access_tool', raise_exception=True)
def upload_and_predict(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        virus_type = request.POST.get('selectedVirus', 'None')

        try:
            # Save the uploaded dataset
            fs = FileSystemStorage(location=settings.UPLOADED_DATASETS_ROOT)
            file_name = fs.save(csv_file.name, csv_file)
            input_file_path = fs.path(file_name)

            # Call prediction logic
            prediction_file, graph_files = process_and_predict(input_file_path, caused_by=virus_type)

            # Prepare paths for rendering
            prediction_file_url = os.path.join(settings.MEDIA_URL, os.path.basename(prediction_file))
            graph_file_urls = [os.path.join(settings.MEDIA_URL, "graphs", os.path.basename(graph)) for graph in graph_files]

            # Load the predictions CSV file
            file_path = os.path.join(settings.MEDIA_ROOT, 'Epidemic_Predictions.csv')
            predictions_df = pd.read_csv(file_path)

            # Extract relevant data
            predictions_data = predictions_df[['Date', 'Active Case', 'Death', 'Predicted Label', 'Prediction Probability']]
            predictions_list = predictions_data.to_dict(orient='records')

            return render(request, 'tool_app/live_result.html', {
                'virus_type': virus_type,
                'prediction_file': prediction_file_url,
                'graphs': graph_file_urls,
                'predictions_data': predictions_list,
                'MEDIA_URL': settings.MEDIA_URL,
                'title': 'Live Result'
            })

        except Exception as e:
            # Handle errors during processing
            return render(request, 'tool_app/tool.html', {
                'error_message': f"An error occurred during processing: {str(e)}",
                'title': 'Live Result'
            })

    # Redirect back to tool page if no file is uploaded
    return render(request, 'tool_app/tool.html', {
        'error_message': "Please upload a dataset to analyze.",
        'title': 'Live Result'
    })


# ======================================================
# 3. Result View for 'specialuser' & 'regularuser' Group
# ======================================================
@login_required(login_url='login')  # Redirect to login if not authenticated
def result_view(request):
    """
    This view handles both authenticated and unauthenticated access to the result page.
    """
    result_file_path = os.path.join(settings.MEDIA_ROOT, 'Epidemic_Predictions.csv')

    if os.path.exists(result_file_path):  # Check if the result file exists
        predictions_df = pd.read_csv(result_file_path)

        # Prepare data for rendering
        predictions_data = predictions_df[['Date', 'Active Case', 'Death', 'Predicted Label', 'Prediction Probability']]
        predictions_list = predictions_data.to_dict(orient='records')

        return render(request,'tool_app/result_view.html', {
            'predictions_data': predictions_list,
            'MEDIA_URL': settings.MEDIA_URL,
            'title': 'Result'
        })
    else:
        # Redirect authenticated group users to no_dataset & tool with a message respected to the group 'regularuser','specialuser'
        if request.user.is_authenticated and request.user.groups.filter(name='regularuser').exists(): #User is authenticated and belongs to regularuser group.
            messages.warning(request, "No data set has been uploaded yet.")
            return redirect('no_dataset')
        
        if request.user.is_authenticated and request.user.groups.filter(name='specialuser').exists(): #User is authenticated and belongs to specialuser group.
            return render(request, 'tool_app/tool.html', {
                'error_message': "Please upload a dataset first to analyze.",
                'title': 'Result'
            })
        if request.user.is_authenticated and request.user.is_superuser: # User is authenticated and is a superuser
            return render(request, 'tool_app/tool.html', {
                'error_message': "Please upload a dataset first to analyze.",
                'title': 'Result'
            })


# ===========================================
# 4. No Dataset View for 'regularuser' Group
# ===========================================    
@login_required(login_url='login')
def no_dataset_view(request):
    data={
        'title':'No_dataset'
    }
    return render(request,"tool_app/no_dataset.html",data)