import os
from sqlalchemy import create_engine

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h")
)

engine = create_engine('sqlite:///' + os.path.join('C:', os.sep, 'Users', 'KhasyRa1','db_local', 'hrdata.db'))
