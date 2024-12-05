import joblib
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from Remote_User.models import ClientRegister_Model, url_detection_type

# Load the pre-trained model and CountVectorizer
phish_model = joblib.load('phishing1.pkl')
cv = joblib.load('count_vectorizer.pkl')

def login(request):
    if request.method == "POST" and 'submit1' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            enter = ClientRegister_Model.objects.get(username=username, password=password)
            request.session["userid"] = enter.id
            return redirect('ViewYourProfile')
        except:
            pass
    return render(request, 'RUser/login.html')

def Add_DataSet_Details(request):
    return render(request, 'RUser/Add_DataSet_Details.html', {"excel_data": ''})

def Register1(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phoneno = request.POST.get('phoneno')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        ClientRegister_Model.objects.create(username=username, email=email, password=password,
                                            phoneno=phoneno, country=country, state=state,
                                            city=city, address=address, gender=gender)
        obj = "Registered Successfully"
        return render(request, 'RUser/Register1.html', {'object': obj})

    return render(request, 'RUser/Register1.html')

def ViewYourProfile(request):
    userid = request.session['userid']
    obj = ClientRegister_Model.objects.get(id=userid)
    return render(request, 'RUser/ViewYourProfile.html', {'object': obj})

def Predict_URL_Type(request):
    if request.method == "POST":
        url_name = request.POST.get('url_name')

        # Debugging: Print the URL name
        print("Input URL:", url_name)

        # Transform the input URL for prediction
        try:
            # Transform the URL directly
            vector1 = cv.transform([url_name])  # No need to call .toarray()
            predict_text = phish_model.predict(vector1)

            # Determine the prediction result
            val = 'Phishing' if predict_text[0] == 'bad' else 'Non-Phishing'

            # Save the prediction result to the database
            url_detection_type.objects.create(url_name=url_name, Prediction=val)

            return render(request, 'RUser/Predict_URL_Type.html', {'objs': val})
        except KeyError as e:
            print("KeyError:", e)
            return render(request, 'RUser/Predict_URL_Type.html', {'objs': 'Error processing the URL.'})
        except Exception as e:
            print("Unexpected error:", str(e))  # Print the full error message
            return render(request, 'RUser/Predict_URL_Type.html', {'objs': 'An unexpected error occurred.'})

    return render(request, 'RUser/Predict_URL_Type.html')
