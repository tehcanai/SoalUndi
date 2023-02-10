import psycopg2
import pandas as pd
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
exclude_words = ["hello", "hi", "thank", "goodbye", "bye"]

def get_Questions() :
    conn_out = psycopg2.connect("dbname=SoalUndiDB user=postgres password=")
    cur = conn_out.cursor()
    cur.execute('SELECT * FROM public."Questions"')
    row = cur.fetchone()
    df = pd.DataFrame([[row[0], row[1]]])

    for row in cur.fetchall():
        df.loc[len(df.index)] = [row[0], row[1]]
    conn_out.close()

    return df

def get_Tokens(df) :
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    word_token =word_tokenize(" ".join(df[1]).lower().translate(remove_punct_dict))
    filtered_token = [w for w in word_token if not w.lower() in stop_words and len(w) > 3]
    filtered_token = [w for w in word_token if not w.lower() in exclude_words and len(w) > 3]

    return filtered_token

def freq_list(tokens) :
    unique_tokens = []
    freq_tokens = []
    for w in tokens :
        if w not in unique_tokens :
            unique_tokens.append(w)
            freq_tokens.append(1)
        else :
            freq_tokens[unique_tokens.index(w)] += 1

    df = pd.DataFrame(tuple(zip(unique_tokens, freq_tokens)))
    df.columns = ['Keywords', 'Frequency']

    return df

def time_series(df) :
    unique_dates = []
    freq_dates = []
    for i in range(len(df)):
        if df.loc[i, 0] not in unique_dates :
            unique_dates.append(df.loc[i, 0])
            freq_dates.append(1)
        else :
            freq_dates[unique_dates.index(df.loc[i, 0])] += 1

    df = pd.DataFrame(tuple(zip(unique_dates, freq_dates)))
    df.columns = ['Dates', 'Frequency']

    return df

def update_keywords(freq_tokens) :
    conn_out = psycopg2.connect("dbname=SoalUndiDB user=postgres password=")
    cur = conn_out.cursor()
    cur.execute('DROP TABLE public."Keywords"')
    cur.execute('CREATE TABLE IF NOT EXISTS public."Keywords"("Keywords" text COLLATE pg_catalog."default" NOT NULL,"Frequency" integer,CONSTRAINT "Keywords_pkey" PRIMARY KEY ("Keywords"))')
    cur.execute('ALTER TABLE IF EXISTS public."Keywords" OWNER to postgres;')
    cols = '","'.join([str(i) for i in freq_tokens.columns.tolist()])

    for i,row in freq_tokens.iterrows():
        try :
            sql = 'INSERT INTO public."Keywords" ("' +cols + '") VALUES (' + '%s,'*(len(row)-1) + '%s)'
            cur.execute(sql, tuple(row))
            conn_out.commit()
        except :
            print("error")

    conn_out.close()






