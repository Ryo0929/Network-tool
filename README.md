# III_Network_Tool

Environment setup
----
### 1. Requirement
- **Python==3.7.6**
- **dash==1.16.3**
- **dash-cytoscape==0.2.0**
- **xlrd==1.2.0**
- **pandas==1.1.3**

----
### 2. Installation

    pip install dash

    pip install dash-cytoscape

    pip install xlrd pandas

----
### 3. How to start
#### At III_Netwrok_Tool folder/dash_cytoscape_master/, run the main.py
    python main.py

#### If the process success, terminal will show this
    Running on http://127.0.0.1:8050/
    Debugger PIN: 139-990-777
    * Serving Flask app "main" (lazy loading)
    * Environment: production
    WARNING: This is a development server. Do not use it in a production deployment.
    Use a production WSGI server instead.
    * Debug mode: on

#### Then go to http://127.0.0.1:8050/. If the graph does not show up, please wait few seconds and reload the page.

----
### 4. Usage
#### Use upload button to upload data file and color file 

![image](https://github.com/Ryo0929/Network-tool/blob/main/readme%20image/chrome-capture%20(1).gif)

![image](https://github.com/Ryo0929/Network-tool/blob/main/readme%20image/chrome-capture%20(2).gif)

#### You can focus a node by clicking the node, and unfocus it using "unfocus" button

![image](https://github.com/Ryo0929/Network-tool/blob/main/readme%20image/chrome-capture%20(5).gif)

#### Change layout, some layouts might take few seconds to process
![image](https://github.com/Ryo0929/Network-tool/blob/main/readme%20image/chrome-capture%20(3).gif)

#### You could change "count" value threshold by adjust the filter
#### Warrning: Seting a too low filter could makes process time very long
![image](https://github.com/Ryo0929/Network-tool/blob/main/readme%20image/chrome-capture%20(4).gif)

----
### 6. Excel input format

### Input file

#### The first sheet should be named edge_count, contaning three column names:'from', 'to' and 'count'
![image](https://github.com/Ryo0929/Network-tool/blob/main/readme%20image/%E6%93%B7%E5%8F%962.PNG)
#### The second sheet should be named node_count, contaning two column names:'tag' and 'count'
#### Warning: Both files must have data and column names to draw the graph
![image](https://github.com/Ryo0929/Network-tool/blob/main/readme%20image/%E6%93%B7%E5%8F%963.PNG)



### Color list file
#### In color list file, the program will get the first sheet as reference. 
#### The first row is color code, which will be taken as color code by words under first row. 
#### For example, 'B99eto-lR0q''s color will be '#FFF529'
![image](https://github.com/Ryo0929/Network-tool/blob/main/readme%20image/%E6%93%B7%E5%8F%964.PNG)
