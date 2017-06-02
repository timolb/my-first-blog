import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from werkzeug.utils import secure_filename

DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


ALLOWED_EXTENSIONS = set(['txt', 'csv', 'db'])

app = Flask(__name__)
#app.config.from_object(__name__)
FieldNamesGl=[]
BPName='flaskr.db'
temprequest=request

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'files'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    rv = sqlite3.connect(os.path.join(app.root_path+'\\files', BPName))
    rv.row_factory = sqlite3.Row
    return rv
	
def init_db(SchName):
    with app.app_context():
        db = get_db()
        with app.open_resource(SchName, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
	
if __name__ == '__main__':
    app.run()

	
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
	
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
		
		

	
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    #return redirect(url_for('show_entries'))
    directory=os.walk(app.root_path+'/files',followlinks=False)
    return render_template('show_entries.html', directory=directory)
	
@app.route('/HandLoadSave', methods=['POST'])
def add_entry2():
 global FieldNamesGl
 if not FieldNamesGl:
  flash('Empty')
 
 answer=0
 StrParam=''
 StrName=''
 flash('uifaeuifeauifae')
 #StrParam=request.form[FieldNamesGl[0]]+request.form[FieldNamesGl[1]]
 for i in FieldNamesGl:
  StrParam+=request.form[i]
  StrName+=i
  if FieldNamesGl.index(i)!=len(FieldNamesGl)-1:
   StrParam+=','
   StrName+=','
  #MasParam.append(int(request.form[i], 10))
 
 db = get_db()
 db.execute('insert into entries ('+StrName+') values ('+StrParam+')')
 cur = db.execute('select * from entries order by id asc')
 entries = cur.fetchall()
 db.commit()
 return render_template('HandLoad.html', FieldNames=FieldNamesGl, StrName=StrName, entries=entries, BPName=BPName)
	
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            #directory=os.walk(app.root_path+'/files',followlinks=False)
            #return render_template('show_entries.html', directory=directory)
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)
	
@app.route('/show_entries', methods=['GET', 'POST'])
def ShowAddFileTemplate():
 entries=[]
 return render_template('show_entries.html', entries=entries)
 
@app.route('/HandLoad', methods=['GET', 'POST'])
def HandLoad():
 return render_template('HandLoad.html')
 
	
	
#Upload Files---------------------------------------------------------	
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/rtjrjt', methods = ['GET', 'POST'])
def upload_file():
 if request.method == 'POST':
  f = request.files['file']
  name = request.form['choice']
  directory=os.walk(app.root_path+'\\files\\',followlinks=False)
  entries=[]
  KolCol=0
  if f and allowed_file(f.filename):
   f.save(app.root_path + '\\files\\' + secure_filename(f.filename))
   name=f.filename
   flash('New file was successfully upload')
  elif name!='':
   flash('There was read from old file')
   
  if name!='':
   if name.rsplit('.', 1)[1]=='db':
    flash('rsgrgrr')
    global BPName
    BPName=name
    #db = get_db()
    #cur = db.execute('select * from entries order by id asc')
    #entries = cur.fetchall()
   else:
    if request.form['Upload']=='Загрузить':
     TempName=name.rsplit('.', 1)[0]+'.db'
     flash(TempName)
     for d, dir, files in directory:
      for file in files:
       if file==TempName:
        BPIsBusy='true'
        return render_template('show_entries.html', BPIsBusy=BPIsBusy, entries=entries, KolCol=KolCol, directory=directory)
     	
   
    MyFile=open(app.root_path +'\\files\\'+name, "r")
    str = MyFile.readline()
    KolCol, StrNames=KolColumnsAndScheme(str, name);
    MyFile=open(app.root_path +'\\files\\'+name, "r")
    CreateTableFromFile(MyFile, KolCol, StrNames)
    MyFile.close()
   
   db = get_db()
   cur = db.execute('select * from entries order by id asc')
   entries = cur.fetchall()
	
    #entries=ReadFromStr(MyFile, KolCol)
  else:
   flash('New file was not upload')
   
 return render_template('show_entries.html', entries=entries, KolCol=KolCol, directory=directory)
 

def CreateTableFromFile(MyFile, KolCol, StrName):
 entries=MyFile.readlines()
 StrParam=''
 i=0
 j=1
 buf=''
 flash(StrName)
 for str in entries:
  for symb in str:
   if i==KolCol:
    break   
   if symb!=';' and symb!=',' and symb!='\n':
    buf=buf+symb
   else:
    StrParam+=buf  #bleee, xz
    if symb!='\n':
     StrParam+=','
    buf=''
    i+=1
  if j==len(entries):
   StrParam+=buf
  db = get_db()
  db.execute('insert into entries ('+StrName+') values ('+StrParam+')')
  db.commit()
  StrParam=''
  i=0
  j+=1
 
 return
 
 
 
 
 
 
 
 
 
 
 
 
def KolColumnsAndScheme(mas, SchName):
 Kol=0
 FieldNames=[]
 StrNames=''
 
 for i in mas:
  if (i=='\n'):
   FieldNames.append(('text'+str(Kol)))
   StrNames+=('text'+str(Kol))
   Kol+=1
   break
  elif i==';' or i==',':
   #KolStr=str(Kol)
   FieldNames.append('text'+str(Kol))
   StrNames+=('text'+str(Kol)+',')
   Kol+=1

 SchName=SchName.rsplit('.', 1)[0]+'.sql'
 MyFile=open(os.path.join(app.root_path,'files\\'+SchName), "w")
 MyFile.write('drop table if exists entries;\ncreate table entries (\n  id integer primary key autoincrement,\n')
 i=1
 FNLen=len(FieldNames)
 
 for param in FieldNames:
  MyFile.write('  '+param+' integer not null')
  if i!=FNLen:
   MyFile.write(',\n')
  else:
   MyFile.write('\n')
  i+=1
 
 MyFile.write(');')
 MyFile.close()
 init_db('files\\'+SchName)
 
 return Kol, StrNames
 
 
def ReadFromStr(MyFile, KolCol):
 mas1=[]
 mas=[]
 buf=''
 i=0
 j=1
 masstr=MyFile.readlines()
 for str in masstr:
  for symb in str:
   if i==KolCol:
    break   
   if symb!=';' and symb!=',' and symb!='\n':
    buf=buf+symb
   else:
    mas1.append(buf)
    buf=''
    i+=1
  if j==len(masstr):
   mas1.append(buf)
  mas.append(mas1)
  mas1=[]
  i=0
  j+=1
 return mas
#End Upload Files-------------------------------------------------------
		
#Create Table--------------------------
@app.route('/HandLoadForm', methods = ['GET', 'POST'])
def Create_Table():
 if request.method == 'POST':
  KolCol=int(request.form['KolCol'], 10)
 
 flash(KolCol)
 FieldNames=[]
 i=0
 while i<KolCol:
  FieldNames.append('text'+str(i))
  i+=1
 global FieldNamesGl
 FieldNamesGl=FieldNames
 Create_Scheme(FieldNames)
 return FieldNames #render_template('HandLoad.html', FieldNames=FieldNames)

@app.route('/HandLoadForm5', methods = ['GET', 'POST'])
def BPCheck():
 if request.method == 'POST':
  if request.form['Create']=='Создать БП':
   global BPName
   BPName=request.form['BPName']
   BPName=BPName+'.db'
   directory=os.walk(os.path.join(app.root_path, 'files'),followlinks=False)
   
   for d, dir, files in directory:
    for i in files:
     if i==BPName:
      return render_template('HandLoad.html', BPIsBusy='true')
   FieldNames=Create_Table()
   
  elif request.form['Create']=='Подтвердить':
   flash('keeek')
   FieldNames=Create_Table()   
 return render_template('HandLoad.html', FieldNames=FieldNames, BPName=BPName)

 
def Create_Scheme(FieldNames):
 ind=BPName.index('.')
 SchName=BPName[0:ind]
 SchName='files\\'+SchName+'.sql'
 MyFile=open(os.path.join(app.root_path,SchName), "w")
 MyFile.write('drop table if exists entries;\ncreate table entries (\n  id integer primary key autoincrement,\n')
 i=1
 FNLen=len(FieldNames)
 
 for param in FieldNames:
  MyFile.write('  '+param+' integer not null')
  if i!=FNLen:
   MyFile.write(',\n')
  else:
   MyFile.write('\n')
  i+=1
 
 MyFile.write(');')
 MyFile.close()
 init_db(SchName)
 return
 
#End Create----------------------------		
		
@app.route('/')
def menu():
    return render_template('menu.html')
	
@app.route('/LookBP',  methods = ['GET', 'POST'])
def LookBP():
 db = get_db()
 cur = db.execute('select * from entries order by id desc')
 entries = cur.fetchall()
 return render_template('LookBP.html', entries=entries)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
	