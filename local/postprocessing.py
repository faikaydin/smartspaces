import datetime
import pandas as pd

#################################################################################


def get_timeline(df):
    return list(df.timestamp.unique())


def Average(lst):
    return sum(lst) / len(lst)


def round_to_min(df):
    df.timestamp = [i.replace(microsecond=0,second=0) for i in df.timestamp]
    return df


def get_single_val_for_time_stamp(df, absolute=True):
    timeline = list(df.timestamp.unique())
    seats = list(df.areaGroupName.unique())
    values = []

    for t in timeline:
        temp = df[df.timestamp == t]
        seat_count = 0
        for x in seats:
            tempx = temp[temp.areaGroupName == x]
            if len(tempx) == 0:
                pass
            elif len(tempx) == 1:
                seat_count += tempx['count'].values[0]
            else:
                seat_count += Average(list(tempx['count']))
        values.append(seat_count)
    if absolute:
        return [i / len(seats) for i in values]
    else:
        return values


def disjointing_time(df):
    time = list(set(df.time))
    time.sort()
    wk = [i.week for i in time]
    day = [i.dayofweek for i in time]
    hr = [i.hour for i in time]
    mint = [i.minute for i in time]
    count = []

    for t in time:
        temp = df[df['time'] == t]
        x = max(temp['count'])
        count.append(int(round_down(x, 10)))
    df = pd.DataFrame()
    df['wk'] = wk
    df['day'] = day
    df['hr'] = hr
    df['min'] = mint
    df['percent'] = count

    return df


def round_down(num, divisor):
    return num - (num%divisor)


def create_training_records(df):
    numberofrecords = len(df)
    records = []

    for i in range(numberofrecords):

        clust = df.iloc[i][5]
        wk = df.iloc[i][0]
        dy = df.iloc[i][1]
        hr = df.iloc[i][2]
        mn = df.iloc[i][3]
        target = df.iloc[i][4]

        temp = df[df.wk == wk - 1]
        temp = temp.reset_index().drop('index', axis=1)
        temp = temp[temp.day == dy]
        temp = temp.reset_index().drop('index', axis=1)
        temp = temp[temp.hr == hr]
        temp = temp.reset_index().drop('index', axis=1)
        temp = temp[temp['min'] == mn]
        temp = temp.reset_index().drop('index', axis=1)
        count_one_wk_ago = temp.percent
        if len(count_one_wk_ago.values) > 0:
            temp = df[df.wk == wk]
            temp = temp.reset_index().drop('index', axis=1)
            if dy != 0:
                temp = temp[temp.day == dy - 1]
            else:
                temp = temp[temp.day == 4]
            temp = temp.reset_index().drop('index', axis=1)
            temp = temp[temp.hr == hr]
            temp = temp.reset_index().drop('index', axis=1)
            temp = temp[temp['min'] == mn]
            temp = temp.reset_index().drop('index', axis=1)
            count_one_day_ago = temp.percent
            if len(count_one_day_ago.values) > 0:
                records.append([clust, wk, dy, hr, mn, count_one_wk_ago.values[0], count_one_day_ago[0], target])

    return records
#################################################################################

# Part I
data = pd.read_csv('data/interim_df.csv')
data = data[data.areaGroupType == 'singleDesk'].reset_index().drop('index', axis=1)
data = data.drop(['areaGroupCapacity', 'areaGroupType'], axis = 1)
data['timestamp'] = pd.to_datetime(data.timestamp)

east = round_to_min(pd.concat([data[data.areaGroupName == 'W.2.138'],
        data[data.areaGroupName == 'W.2.001'],
        data[data.areaGroupName == 'W.2.002'],
        data[data.areaGroupName == 'W.2.003'],
        data[data.areaGroupName == 'W.2.004'],
        data[data.areaGroupName == 'W.2.005'],
        data[data.areaGroupName == 'W.2.006'],
        data[data.areaGroupName == 'W.2.007'],]).sort_values('timestamp').reset_index().drop('index', axis = 1))

west = round_to_min(pd.concat([data[data.areaGroupName == 'W.2.089'],
        data[data.areaGroupName == 'W.2.090'],
        data[data.areaGroupName == 'W.2.091'],
        data[data.areaGroupName == 'W.2.092'],
        data[data.areaGroupName == 'W.2.093'],
        data[data.areaGroupName == 'W.2.094']]).sort_values('timestamp').reset_index().drop('index', axis = 1))

northwest = round_to_min(pd.concat([data[data.areaGroupName == 'W.2.096'],
        data[data.areaGroupName == 'W.2.097'],
        data[data.areaGroupName == 'W.2.098'],
        data[data.areaGroupName == 'W.2.099'],
        data[data.areaGroupName == 'W.2.100']]).sort_values('timestamp').reset_index().drop('index', axis = 1))

southwest = round_to_min(pd.concat([data[data.areaGroupName == 'W.2.079'],
        data[data.areaGroupName == 'W.2.080'],
        data[data.areaGroupName == 'W.2.081'],
        data[data.areaGroupName == 'W.2.077'],
        data[data.areaGroupName == 'W.2.076']]).sort_values('timestamp').reset_index().drop('index', axis = 1))

east_ = get_single_val_for_time_stamp(east)
west_ = get_single_val_for_time_stamp(west)
northwest_ = get_single_val_for_time_stamp(northwest)
southwest_ = get_single_val_for_time_stamp(southwest)
east_time = get_timeline(east)
west_time = get_timeline(west)
northwest_time = get_timeline(northwest)
southwest_time = get_timeline(southwest)

data_ = (east_, west_, northwest_, southwest_)
time_ = (east_time, west_time, northwest_time, southwest_time)

j = 0
for i in ['east', 'west', 'northwest', 'southwest']:
    temp = pd.DataFrame()
    temp['time'] = time_[j]
    temp['count'] = data_[j]
    temp.to_csv('data/' + i + '.csv')
    j += 1

# end


# Part II
east = pd.read_csv('data/east.csv').drop('Unnamed: 0', axis = 1)
east.time = pd.to_datetime(east.time)

west = pd.read_csv('data/west.csv').drop('Unnamed: 0', axis = 1)
west.time = pd.to_datetime(west.time)

southwest = pd.read_csv('data/southwest.csv').drop('Unnamed: 0', axis = 1)
southwest.time = pd.to_datetime(southwest.time)

northwest = pd.read_csv('data/northwest.csv').drop('Unnamed: 0', axis = 1)
northwest.time = pd.to_datetime(northwest.time)

east_ = [i for i in east['count']]
west_ = [i for i in west['count']]
southwest_ = [i for i in southwest['count']]
northwest_ = [i for i in northwest['count']]
east_t = list(east['time'])
west_t = list(west['time'])
southwest_t = list(southwest['time'])
northwest_t = list(northwest['time'])
# time floor
east.time = [i.floor('10T') for i in east.time]
west.time = [i.floor('10T') for i in west.time]
northwest.time = [i.floor('10T') for i in northwest.time]
southwest.time = [i.floor('10T') for i in southwest.time]
# fix over crowd
east['count'] = [100 if i > 1 else int(round_down(round(100*i), 10)) for i in east['count']]
west['count'] = [100 if i > 1 else int(round_down(round(100*i), 10)) for i in west['count']]
northwest['count'] = [100 if i > 1 else int(round_down(round(100*i), 10)) for i in northwest['count']]
southwest['count'] = [100 if i > 1 else int(round_down(round(100*i),10)) for i in southwest['count']]
east = disjointing_time(east)
west = disjointing_time(west)
northwest = disjointing_time(northwest)
southwest = disjointing_time(southwest)
east['c'] = 0
west['c'] = 1
northwest['c'] = 2
southwest['c'] = 3
east_records = create_training_records(east)
west_records = create_training_records(west)
northwest_records = create_training_records(northwest)
southwest_records = create_training_records(southwest)
east_df = pd.DataFrame.from_records(east_records, columns=['cluster', 'week', 'day', 'hour',
                                                      'minute', 'wk_ago', 'day_ago', 'target'])
west_df = pd.DataFrame.from_records(west_records, columns=['cluster', 'week', 'day', 'hour',
                                                      'minute', 'wk_ago', 'day_ago', 'target'])
northwest_df = pd.DataFrame.from_records(northwest_records, columns=['cluster', 'week', 'day', 'hour',
                                                      'minute', 'wk_ago', 'day_ago', 'target'])
southwest_df = pd.DataFrame.from_records(southwest_records, columns=['cluster', 'week', 'day', 'hour',
                                                      'minute', 'wk_ago', 'day_ago', 'target'])

records_df = pd.concat([east_df, west_df, northwest_df, southwest_df])
records_df = records_df.reset_index().drop('index', axis=1)
records_df.to_csv('data/records_for_the_network.csv')
# end
