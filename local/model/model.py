from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn import preprocessing
import pandas as pd
import numpy as np

min_max_scaler = preprocessing.MinMaxScaler()


def sink_days(c0):
    n_days = list(c0.day.unique())
    n_hrs = list(c0.hour.unique())
    fill = pd.DataFrame(data=None, index=n_hrs, columns=n_days)
    col = 0
    for d in n_days:
        n_vec = []
        for h in n_hrs:
            temp = c0[c0['day'] == d]
            temp = temp[temp['hour'] == h]
            n_vec.append(max(list(temp.prediction)))
        fill.iloc[:, col] = n_vec
        col += 1

    return fill


data = pd.read_csv('data/records_for_the_network.csv').drop('Unnamed: 0', axis=1)
traindf = data[data['week'] != 40]
test = data[data['week'] == 40]
traindf = traindf.reset_index()
test = test.reset_index()
traindf['target'].value_counts().plot(kind='bar').plot

final_targets = []
final_targets_ = []

for i in traindf.target:
    if i < 40:
        final_targets.append(0)
        final_targets_.append('empty')
    else:
        final_targets.append(1)
        final_targets_.append('busy')

train_y = np.array(final_targets)
traindf['target_verbose'] = final_targets_

final_targets = []
final_targets_ = []
for i in test.target:
    if i < 40:
        final_targets.append(0)
        final_targets_.append('empty')
    else:
        final_targets.append(1)
        final_targets_.append('busy')

test_y = np.array(final_targets)
test['target_verbose'] = final_targets_

traindf = traindf.drop('week', axis=1)
traindf['day'] = traindf['day'].astype('category')
traindf['hour'] = traindf['hour'].astype('category')
traindf['minute'] = traindf['minute'].astype('category')
traindf['cluster'] = traindf['cluster'].astype('category')
traindf['wk_ago'] = min_max_scaler.fit_transform(np.array(traindf['wk_ago']).reshape(-1, 1))
traindf['day_ago'] = min_max_scaler.fit_transform(np.array(traindf['day_ago']).reshape(-1, 1))

test = test.drop('week', axis=1)
test['day'] = test['day'].astype('category')
test['hour'] = test['hour'].astype('category')
test['minute'] = test['minute'].astype('category')
test['cluster'] = test['cluster'].astype('category')
test['wk_ago'] = min_max_scaler.fit_transform(np.array(test['wk_ago']).reshape(-1, 1))
test['day_ago'] = min_max_scaler.fit_transform(np.array(test['day_ago']).reshape(-1, 1))

dumb_day = pd.get_dummies(traindf.day)
dumb_hour = pd.get_dummies(traindf.hour)
dumb_minute = pd.get_dummies(traindf.minute)
dumb_cluster = pd.get_dummies(traindf.cluster)

dumb_daytest = pd.get_dummies(test.day)
dumb_hourtest = pd.get_dummies(test.hour)
dumb_minutetest = pd.get_dummies(test.minute)
dumb_clustertest = pd.get_dummies(test.cluster)

train_x = []
for i in range(len(traindf)):
    record_x = []
    for j in dumb_day.iloc[i, :]:
        record_x.append(j)
    for j in dumb_hour.iloc[i, :]:
        record_x.append(j)
    for j in dumb_minute.iloc[i, :]:
        record_x.append(j)
    for j in dumb_cluster.iloc[i, :]:
        record_x.append(j)
    record_x.append(traindf['wk_ago'][i])
    record_x.append(traindf['day_ago'][i])

    train_x.append(record_x)

test_x = []
for i in range(len(test)):
    record_x = []
    for j in dumb_daytest.iloc[i, :]:
        record_x.append(j)
    for j in dumb_hourtest.iloc[i, :]:
        record_x.append(j)
    for j in dumb_minutetest.iloc[i, :]:
        record_x.append(j)
    for j in dumb_clustertest.iloc[i, :]:
        record_x.append(j)
    record_x.append(test['wk_ago'][i])
    record_x.append(test['day_ago'][i])

    test_x.append(record_x)

clf = GradientBoostingClassifier(learning_rate=0.01).fit(train_x, train_y)
accuracy_score(test_y, clf.predict(test_x))
xa = clf.predict_proba(test_x)
xa = [round(i[1], 3) for i in xa]
test['prediction'] = xa
results_Df = [sink_days(test[test.cluster == i]) for i in list(test.cluster.unique())]
#############
counter = 0
for i in results_Df:
    i.to_csv('data/cluster' + str(counter) + 'prediction.csv')
    counter +=1