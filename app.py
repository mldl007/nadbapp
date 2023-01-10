import numpy as np
import pandas as pd
from dateutil import parser
from flask import Flask, render_template
from flask_cors import cross_origin, CORS
from db_operations.db_operations import DBOperations

app = Flask(__name__)
CORS(app)


def date_time_parser(dt):
    """
    Computes the minutes elapsed since published time.
    :param dt: date
    :return: int, minutes elapsed.
    """
    return int(np.round((dt.now(dt.tz) - dt).total_seconds() / 60, 0))


def elapsed_time_str(mins):
    """
    Return the time elapsed string from minutes passed as an argument.
    :param mins: int, minutes elapsed.
    :return: str, time elapsed string
    """
    time_str = ''
    hours = int(mins / 60)
    days = np.round(mins / (60 * 24), 1)
    remaining_mins = int(mins - (hours * 60))
    if days >= 1:
        time_str = f'{str(days)} days ago'
        if days == 1:
            time_str = 'a day ago'
    elif (days < 1) & (hours < 24) & (mins >= 60):
        time_str = f'{str(hours)} hours and {str(remaining_mins)} mins ago'
        if (hours == 1) & (remaining_mins > 1):
            time_str = f'an hour and {str(remaining_mins)} mins ago'
        if (hours == 1) & (remaining_mins == 1):
            time_str = f'an hour and a min ago'
        if (hours > 1) & (remaining_mins == 1):
            time_str = f'{str(hours)} hours and a min ago'
        if (hours > 1) & (remaining_mins == 0):
            time_str = f'{str(hours)} hours ago'
        if ((mins / 60) == 1) & (remaining_mins == 0):
            time_str = 'an hour ago'
    elif (days < 1) & (hours < 24) & (mins == 0):
        time_str = 'Just in'
    else:
        time_str = f'{str(mins)} minutes ago'
        if mins == 1:
            time_str = 'a minute ago'
    return time_str


@app.route("/")
@cross_origin()
def index():
    """
    Entry point
    """
    try:
        db = DBOperations()
        final_df = db.read_news_from_db()
        if len(final_df) > 1:
            final_df["parsed_date"] = final_df["parsed_date"].map(parser.parse)
            final_df["elapsed_time"] = final_df["parsed_date"].apply(date_time_parser)
            final_df = final_df.loc[final_df["elapsed_time"] <= 1440, :].copy()
            final_df["elapsed_time_str"] = final_df["elapsed_time"].apply(elapsed_time_str)
            final_df.sort_values(by="elapsed_time", inplace=True)
            final_df['src_time'] = final_df['src'] + ("&nbsp;" * 5) + final_df["elapsed_time_str"]
            final_df.drop(columns=['_id', 'parsed_date', 'src', 'elapsed_time', 'elapsed_time_str'], inplace=True)
            final_df.drop_duplicates(subset='description', inplace=True)
            final_df = final_df.loc[(final_df["title"] != ""), :].copy()
        else:
            final_df = pd.DataFrame({'title': '', 'url': '',
                                     'description': '', 'src_time': ''}, index=[0])
    except:
        final_df = pd.DataFrame({'title': '', 'url': '',
                                 'description': '', 'src_time': ''}, index=[0])

    result_str = '''
                    <div class="box"><form> 
                    <div class="banner">
                    <h1>Latest News</h1>
                    </div><br>
                 '''

    for n, i in final_df.iterrows():  # iterating through the search results
        href = i["url"]
        description = i["description"]
        url_txt = i["title"]
        src_time = i["src_time"]
        result_str += f'''<div>
                          <a href="{href}" target="_blank" class="headline">{url_txt}
                          </a>
                          </div>
                          <div>
                          <a href="{href}" target="_blank" class="description">
                          {description}
                          </a>
                          </div>
                          <div>
                          <a href="{href}" target="_blank" class="time">
                          {src_time}
                           </a>
                           </div>
                           <div>
                           <p></p>
                           </div>
                           '''

    result_str += '</form></div>'
    return render_template("index.html", body=result_str)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
    