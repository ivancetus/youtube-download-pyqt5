
### some info
- [Reference](http://mahaljsp.asuscomm.com/index.php/2020/08/28/youtube_download/)  

- UI layout is based on another app, `stocx_download` which is a web crawler that read pages on an online novel website, download text as txt.

- To modify UI layout, open qtDesigner, select file `ui/ui_mainwindow.ui`, compile .ui using a custom tool. 

- Set up a custom tool (using PyCharm) to compile .ui into .py

1. Open file setting `Ctrl + Alt + S`
2. Tools / External Tools / Add
3. Name: pyUic
4. Program: C:\myproject\venv\Scripts\pyuic5.exe `select pyuic5.exe inside project venv`
5. Arguments: $FileName$ -o $FileNameWithoutExtension$.py
6. Working Directory: $ProjectFileDir$\ui

- right click on .ui, tools / external tools / pyUic

- provide custom `img/favicon.ico` if you want it to show on the app

- execute `pic_to_string.py` 

- execute pyinstaller on your system, need to have every package installed as in venv 

```commandline
cd C:\myproject

pyinstaller --hidden-import=queue -w -F MainWindow.py
```
-w => not showing the debug window, might cause the program unable to initiate webdriver manager

### this section maybe obsolete
\venv\lib\site-packages\pytube\cipher.py  
change from:  
var_regex = re.compile(r"^\w+\W")  
to:  
var_regex = re.compile(r"^\$*\w+\W") 