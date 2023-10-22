# %% [markdown]
# ### Model Creation

# %%
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
import smtplib
from dotenv import load_dotenv
import os
import base64
import requests
from sklearn.metrics import f1_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
import seaborn as sns
from keras.utils.vis_utils import plot_model
from sklearn.metrics import accuracy_score
from tensorflow.keras import layers
from tensorflow import keras
from sklearn.preprocessing import StandardScaler  # scaling of the data
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest  # feature selection
import tensorflow as tf
import numpy as np
import pandas as pd

# %%
tf.config.list_physical_devices('GPU')

# %%
tf.test.is_built_with_cuda()

# %%
dataset = pd.read_csv(
    "./MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv")
feature_list = dataset.columns.values
dataset

# %%
dataset.shape
dataset = dataset.replace(np.inf, np.nan)    # replacing inf with nan
# ghen converting nan to mean values
dataset = dataset.fillna(dataset.mean(numeric_only=True))

# %%
X = dataset.iloc[:, :-1].values
print("shape of X", X.shape)

Y = dataset.iloc[:, -1].values
print("shape of Y", Y.shape)

# %%
# to check whether the array contains nan
print("is NaN present:", np.any(np.isnan(X)))
# to check whether the array contains inf
print("is inf present:", np.any(np.isinf(X)))
X[X < 0] = 0   # to replace all negative values with zeros

# %%

# %%
bestfeatures = SelectKBest(score_func=mutual_info_classif, k=50)
fit = bestfeatures.fit(X, Y)
# create df for scores
dfscores = pd.DataFrame(fit.scores_)
# create df for column names
dfcolumns = pd.DataFrame(feature_list)

# concat two dataframes for better visualization
featureScores = pd.concat([dfcolumns, dfscores], axis=1)

# naming the dataframe columns
featureScores.columns = ['Selected_columns', 'Score_chi2']
# print 50 best features
print(featureScores.nlargest(50, 'Score_chi2'))


# %%
# print(featureScores.nlargest(50,'Score_chi2').Selected_columns.values)
featureScore_after_filter = featureScores.nlargest(50, 'Score_chi2')
print(featureScore_after_filter.index[0])
count = 0
ind = []
for i in featureScore_after_filter.Score_chi2:
    if i < 0.2:
        ind.append(featureScore_after_filter.index[count])
    count = count + 1
featureScore_after_filter = featureScore_after_filter.drop(
    ind, axis=0)  # contains all the filtered features
X = pd.DataFrame(X)
# contains data after filter from feature selection
X = X.loc[:, featureScore_after_filter.index]
print(X)

# %%
labelencoder_y = LabelEncoder()
Y = labelencoder_y.fit_transform(Y)

# %% [markdown]
# ### Training of the Model

# %%
x_train, x_test, y_train, y_test = train_test_split(
    X, Y, test_size=0.2, random_state=0)

# %%

scaler_X = StandardScaler()
x_train_scaled = scaler_X.fit_transform(x_train)  # preprocessed training data
x_test_scaled = scaler_X.fit_transform(x_test)  # preprocessed testing data

# %%
model = keras.Sequential([
    keras.layers.Dense(64, input_shape=(45,), activation='relu'),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(2, activation='sigmoid')
])


# %%
# to save weights in the middle of a session
model.save_weights('./checkpoints/')

# %%
# Compiling the model
model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])


# %%
# fitting the model
model.fit(x_train_scaled, y_train, epochs=10, batch_size=64)

# %%
model.save('Weights/Model_1')  # to save weights as an entire weights

# or this is as well works but it stores it in diff format
# model.save('Weights_in_h5_format/weights_1.h5')

# %%
model.evaluate(x_test_scaled, y_test, 64)

# %%
y_pred = model.predict(x_test_scaled, 64)
y_pred = np.argmax(y_pred, axis=1)
y_pred

# %%
accuracy_score(y_test, y_pred)

# %%
# model.predict(x_test_scaled[2].reshape(1,-1))
# x_test_scaled[2].reshape(1,-1)

# %% [markdown]
# ### Model Demonstration

# %%
# to test a particular value on when recieved from IOT device
X_recieved = dataset.iloc[18885, :-1].values
X_recieved = pd.DataFrame(X_recieved)
X_recieved = X_recieved.loc[featureScore_after_filter.index, :]
X_recieved = np.array(X_recieved).reshape(1, -1)
X_recieved = np.asarray(X_recieved).astype(np.float32)

# %%
loadModel = tf.keras.models.load_model('Weights_in_h5_format/weights_1.h5')

# %%
loadModel.summary()

# %%
plot_model(loadModel, to_file='model_plot.png',
           show_shapes=True, show_layer_names=True)

# %%
pred = loadModel.predict(X_recieved)
pred

# %%
y_pred = loadModel.predict(x_test_scaled, 64)
y_pred = np.argmax(y_pred, axis=1)
y_pred

# %%
# confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(cm)

# %%
# heatmap of confusion matrix
sns.heatmap(cm/np.sum(cm), annot=True, fmt='.2%', cmap='Blues')

# %%
precision_score(y_test, y_pred)

# %%
recall_score(y_test, y_pred)

# %%
f1_score(y_test, y_pred)

# %%
# SMS service

if(pred[0][1] == 1):  # 1 - ddos     0 - benign
    load_dotenv()
    appId = os.getenv('APPID')
    accessKey = os.getenv('ACCESSKEY')
    accessSecret = os.getenv('ACCESSSECRET')
    projectId = os.getenv('PROJECTID')
    channel = "SMS"
    identity = "+918792884722"
    url = "https://us.conversation.api.sinch.com/v1/projects/" + \
        projectId + "/messages:send"

    data = accessKey + ":" + accessSecret
    encodedBytes = base64.b64encode(data.encode("utf-8"))
    accessToken = str(encodedBytes, "utf-8")

    payload = {
        "app_id": appId,
        "recipient": {
            "identified_by": {
                "channel_identities": [
                    {
                        "channel": channel,
                        "identity": identity
                    }
                ]
            }
        },
        "message": {
            "text_message": {
                "text": "Ddos Attack Detected. Kindly take necessary action."
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + accessToken
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    print(data)

# %%
# Email service


if(pred[0][1] == 1):
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login("adigupta239@gmail.com", "mxwzguwzdcxcrqdw")

    # message to be sent
    subject = "Suspicious activity detected on your network"
    text = 'Dear user, our model have detected some malicious traffic on your network which could be a possible attempt of a DDOS attack. You can perform the following action :\n \n 1.Disconnect all your devices from the network.\n 2.Check if any unknown software is installed on your device. \n 3.Contact a security personnel ASAP. \n  \nHope you find this alert helpful and took the action at right time.'

    message = 'Subject: {}\n\n{}'.format(subject, text)

    # sending the mail
    s.sendmail("adigupta239@gmail.com", "arcyjain2002@gmail.com", message)

    # terminating the session
    s.quit()
