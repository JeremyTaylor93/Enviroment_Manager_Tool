# randomize selected objects

# or instance selected objects and then randomize

# or instance selected objects, group and then randomize group 


import pymel.core as pm
import maya.cmds as cmds
import random as rand

from functools import partial

import maya.mel as mel

import os

project = pm.workspace(q=True,act=True)

scriptsFilePath = project + '/scripts'

FilePath = []

nameIncrements = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']


class EnviromentManagerWindow():
    

    def __init__(self):

		self.windowName = 'EnviromentManager_v001'
		self.windowWidth = 300
		self.windowHeight = 1100
		self.objectList = []
		self.enviromentLayersList = []
		self.widgets = {}
		self.rootObject = 'ROOT_enviroment_01'
		self.FilePath = pm.workspace.path
		
		
		self.create(self.windowName, self.windowWidth, self.windowHeight)

    def create(self, windowName, windowWidth, windowHeight):
		
        if pm.objExists('ROOT_enviroment_01'):
            self.rootObject = 'ROOT_enviroment_01'
        else:
            pm.group(n='ROOT_enviroment_01', em=True)
            pm.select(cl=True)
            self.rootObject = 'ROOT_enviroment_01'

        # delete window if it exsists
        if pm.window("window", exists=True):
            pm.deleteUI("window")

        #define window
        self.widgets['window'] = pm.window("window", t=windowName, w=windowWidth, h=windowHeight, menuBar = True,titleBarMenu=True,bgc=[0.18,0.18,0.18],maximizeButton=False)

        pm.menu( label='File', tearOff=True )
        pm.menuItem( label='Quit', c = partial(self.quit, "AutoRig_JT"))
        pm.menu( label='Help', helpMenu=True )
        pm.menuItem( 'Application..."', label='About Creator', c = self.about )
        pm.menuItem( 'Instructions', label='Instructions', c = self.instructions )

        self.widgets['mainLayout'] = pm.columnLayout(adj=True)


        pm.frameLayout('Import/Export tools',cll=True,bgc=[0.25,0.25,0.25])

        #pm.button(l='Browse >>>', c= self.fileBrowser,bgc=[0.1,0.1,0.1],h=50)

        pm.separator(h=15)
        FilePathText = pm.text('FilePathText',l=self.FilePath,bgc=[0.1,0.1,0.1],h=50)
        pm.separator(h=15)
        projectsOptionMenu = pm.optionMenu("library_Menu", w=300,label = "Choose a Folder:   ",cc= partial(self.populateObjects),bgc=[0.1,0.1,0.1])
        pm.separator(h=15)

        #create character option
        characterOptionMenu = pm.optionMenu("Contents_Menu", w=300,label = "Choose a Object:",bgc=[0.1,0.1,0.1])

        self.populateFolders()
        self.populateObjects() 
        pm.separator(h=15)
        CreateCharacterButton = pm.button(l="Build",w=300,h=50,c=self.build,bgc=[0.1,0.1,0.1])

        exportSelectionButton = pm.button(l="Export_Selection",w=300,h=50,c=self.ExportSelection,bgc=[0.1,0.1,0.1])
        pm.setParent(u=True)
        pm.separator(style='none',h=10)


        pm.frameLayout('Placement tools',cll=True,bgc=[0.25,0.25,0.25])
        
        pm.text(l='Randomize Placement:')
        pm.separator(style='none',h=10)
        
        pm.rowColumnLayout(nc=2)
        pm.text(l='                               number of instances here:')
        self.widgets['numberOfInstances'] = pm.intField('numberOfInstances',v=5,w=50,bgc=[0.1,0.1,0.1])

        pm.text(l='                 randomize radius:')
        self.widgets['randomizeRadius'] = pm.intField('randomizeRadius',v=5,w=50,bgc=[0.1,0.1,0.1])

        

        pm.text(l='                     randomize scale max:')
        self.widgets['randomizeScaleMAX'] = pm.floatField('randomizeScaleMAX',v=1,bgc=[0.1,0.1,0.1])

        pm.text(l='                     randomize scale min:')
        self.widgets['randomizeScaleMIN'] = pm.floatField('randomizeScaleMIN',v=-1,bgc=[0.1,0.1,0.1])
        
        pm.separator(style='none',h=10)
        pm.separator(style='none',h=10)
        pm.setParent(u=True)
        pm.button(l='Randomize',c= self.randomize)
        pm.separator(style='none',h=10)

        pm.text(l='Attach along path:')
        pm.separator(style='none',h=10)
        pm.rowColumnLayout(nc=2)
        
        pm.text(l='numberOfDuplicates:')
        self.widgets['numberOfDuplicates'] = pm.intField('numberOfDuplicates',v=5,w=50,bgc=[0.1,0.1,0.1])
        pm.text(l='set curve to duplicate along:')
        self.widgets['curvePath'] = pm.textFieldButtonGrp('curvePath',bl='<<<',bc=self.addCurve)
        pm.text(l='Randomize:')
        self.widgets['RandomPathDistance'] = pm.checkBox(l='')
        pm.text(l='                     randomize scale max:')
        self.widgets['randomizeScaleMINPath'] = pm.floatField('randomizeScaleMINPath',v=-1,bgc=[0.1,0.1,0.1])
        pm.text(l='                     randomize scale min:')
        self.widgets['randomizeScaleMAXPath'] = pm.floatField('randomizeScaleMAXPath',v=1,bgc=[0.1,0.1,0.1])
        
        
        pm.setParent(u=True)
        pm.button(l='Attach to path',c= self.duplicateAlongPath)

        
        pm.rowColumnLayout(nc=2)
        pm.text(l='             set ground plane :')
        self.widgets['groundplaneTextField'] = pm.textFieldButtonGrp('groundPlaneTextField',bl='<<<',bc=self.addGroundPlane)
        pm.setParent(u=True)
        pm.button(l='Snap to ground',c = self.snapToGround)
        
        pm.setParent(u=True)
        pm.separator(style='none',h=10)
        pm.frameLayout('Renaming tools',cll=True,bgc=[0.25,0.25,0.25])
        
        self.widgets["replaceOptions"] = pm.radioButtonGrp( numberOfRadioButtons=3, label='replace options:', labelArray3=['replace search', 'replace before', 'replace after'],sl=1 )
	
        self.widgets["selectionOptions"] = pm.radioButtonGrp( numberOfRadioButtons=3, label='selection options:', labelArray3=['hierarchy', 'selected', 'all'], sl=2 )

        self.widgets["rowLayout"] = pm.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 250)] )
        
        pm.text( label='search for:' )
        self.widgets["searchField"] = pm.textField()
        
        pm.text( label='replace for:' )
        self.widgets["replaceField"] = pm.textField()
        
        pm.separator(h=20,style='none')
        pm.button(l='GO',c=self.GO)
        pm.separator(h=20,style='none')
        pm.separator(h=20,style='none')
        pm.separator(h=20,style='none')
        pm.button(l='Increment Chain',c=self.renameChain)

        # create window
        pm.showWindow(self.widgets['window'])
        pm.window(self.widgets['window'],e=True,w=windowWidth,h=windowHeight,s=False)
    
    def fileBrowser(self,*args):
        singleFilter = "All Files (*.*)"
        Path = pm.fileDialog2(fileFilter=singleFilter, dialogStyle=2,fm=2)
        self.FilePath = Path
        pm.text('FilePathText',e=True,l=Path[0])
        print FilePath
        self.populateFolders()
        self.populateObjects()
                
    def populateFolders(self,*args):
        projectPath = pm.text('FilePathText',q=True,l=True)
        print projectPath
        projects = os.listdir(projectPath)

        for project in projects :
            if project == '.DS_Store':
                print 'ignore'
            elif project == 'workspace.mel':
                print 'ignore'
            else:
                pm.menuItem(label = project, parent = "library_Menu" )
            print project

    def populateObjects(self,*args):

        ProjectPath = pm.text('FilePathText',q=True,l=True)
        
        menuItems = pm.optionMenu("Contents_Menu", q=True, itemListLong = True)
        print 'MENU ITEMS LIST :'
        print  menuItems

        if menuItems != None:
            for item in menuItems:
                pm.deleteUI(item)
        selectedProject = pm.optionMenu("library_Menu",q=True,v=True)
        print selectedProject
        projectPath = ProjectPath + "/"+selectedProject+"/"

        files = os.listdir(projectPath)

        characters = []

        for file in files:
            
            if file.rpartition(".")[2] == "mb":
                characters.append(file)

        for character in characters:
            niceName = character.rpartition(".")[0]
            pm.menuItem(label = character, parent = "Contents_Menu")

    def build(self,*args):
        ProjectPath = pm.text('FilePathText',q=True,l=True)
        selectedProject = pm.optionMenu("library_Menu",q=True,v=True)
        FolderPath = ProjectPath + "/"+selectedProject+"/"
        selectedCharacter = pm.optionMenu("Contents_Menu",q=True,v=True)
        filePath = FolderPath + selectedCharacter
        print filePath
        cmds.file(filePath,i=True,iv=True)
    def ExportSelection(self,*args):
        singleFilter = "All Files (*.*)"
        Path = pm.fileDialog2(fileFilter=singleFilter, dialogStyle=2,fm=2)
        # list selection in array
        list = pm.ls(sl=True)
        # get filename from user
        result = pm.promptDialog(
                title='Rename Object',
                message='Enter Name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
        if result == 'OK':
            fileName = pm.promptDialog(query=True, text=True)
            print fileName
            # export file
            pm.exportSelected(Path[0]+'/'+fileName+'.mb')
        else:
            pm.warning('export canceled!')	
    def snapToGround(self,*args):


        groundPlaneObject = pm.textFieldButtonGrp(self.widgets['groundplaneTextField'],q=True,tx=True)
        list = pm.ls(sl=True,tr=True)

        for x in list :
            
            locator = pm.spaceLocator()
            group = pm.group(locator)
            pm.delete(pm.parentConstraint(x,group,mo=False))
            Xparent = x.getParent()
            pm.parent(x,locator)
            pm.transformLimits(locator, tx=[0, 0] ,etx=[1, 1])
            pm.transformLimits(locator, tz=[0, 0] ,etz=[1, 1])
            pm.delete(pm.geometryConstraint(groundPlaneObject,locator,w=1))
            pm.parent(x,Xparent)
            pm.delete(group)
        
    def addGroundPlane(self,*args):
        object = pm.ls(sl=True)[0]
        print object
        pm.textFieldButtonGrp(self.widgets['groundplaneTextField'],e=True,tx=object)
    
    def addCurve(self,*args):
        object = pm.ls(sl=True)[0]
        print object
        pm.textFieldButtonGrp(self.widgets['curvePath'],e=True,tx=object)
    def selectedObjects(self,*args):

        list = pm.ls(sl=True, tr=True)

        return list

    def instanceObjects(self,*args):

        input_numberOfInstances = pm.intField(self.widgets[''], q=True, v=True)

        list = pm.ls(sl=True, tr=True)

        for object in list :

            objectName = object

            instanceName = 'INST' + objectName.rpartition('GEO')[2]

            for i in range(input_numberOfInstances):


                pm.select(object,r=True)
                name = pm.instance(n=instanceName)

                self.objectList.append(name[0])

        return self.objectList


    def instanceObjectsGroup(self,*args):


        list = pm.ls(sl=True, tr=True)
        input_numberOfInstances = pm.intField(self.widgets['numberOfInstances'], q=True, v=True)
        groupName = ''
        instanceList = []
        for i in range(input_numberOfInstances):
            instanceList = []
            for object in list:
                objectName = object
                searchName = objectName.rpartition('GEO')[2]
                searchName = searchName.rpartition('_0')[0]
                groupSearchName = 'GRP'+searchName+'*'
                pm.select('*'+searchName+'*',r=True)
                if pm.objExists('GRP'+searchName+'*'):
                    pm.select('*'+'GRP_'+'*',d=True)
                ListExsistingDuplicates = pm.ls(sl=True,tr=True)
                numberExsistingDuplicates = len(ListExsistingDuplicates)
                instanceName = 'INST' + objectName.rpartition('GEO')[2] 
                instanceName = instanceName.rpartition('_0')[0] +'_'+str(numberExsistingDuplicates)
                groupName = 'GRP' + instanceName.rpartition('INST')[2]
                pm.select(object, r=True)
                pm.instance(n=instanceName)
                name = pm.ls(sl=True)
                        
                # add identifier 
                pm.addAttr(name[0], ln="Instance", dt="string", h = True  )
                instanceList.append(name[0])
            
            pm.group(instanceList, n=groupName)
            
            pm.parent(groupName, self.rootObject)
            self.objectList.append(groupName)
        pm.select(list,r=True)
        return self.objectList



    def randPlacement(self,objectList,*args):

        input_randomizeRadius = pm.intField(self.widgets['randomizeRadius'], q=True, v=True)

        max = input_randomizeRadius

        min = input_randomizeRadius * -1

        # loop through
        for object in objectList :

            # spread
            randomNumberX = rand.randint(min, max)
            randomNumberZ = rand.randint(min, max)

            randomRotate = rand.randint(0,360)

            randomScale = rand.uniform((pm.floatField(self.widgets['randomizeScaleMIN'],q=True,v=True)),(pm.floatField(self.widgets['randomizeScaleMAX'],q=True,v=True)))

            pm.setAttr(object+'.tx', randomNumberX)
            pm.setAttr(object+'.tz', randomNumberZ)

            pm.setAttr(object+'.ry', randomRotate)

            pm.setAttr(object+'.sx', randomScale)
            pm.setAttr(object+'.sy', randomScale)
            pm.setAttr(object+'.sz', randomScale)

    def randomize(self,*args):

        list = self.instanceObjectsGroup()
        self.randPlacement(list)
        self.objectList = []
    def GO(self,*args):
	
        replaceOption = pm.radioButtonGrp(self.widgets["replaceOptions"],q=True,sl=True)
        selectionOption = pm.radioButtonGrp(self.widgets["selectionOptions"],q=True,sl=True)
        
        searchString = pm.textField(self.widgets["searchField"],q=True,tx=True)
        replaceString = pm.textField(self.widgets["replaceField"],q=True,tx=True)
        
        # if no replace option selected
        if replaceOption == 0:
            pm.warning('please select an option!')
        # if replace option selected
        elif replaceOption == 1:
            # if option hiearchy 
            if selectionOption == 1:
                pm.select(hi=True)
                list = pm.ls(sl=True)
                for x in list:
                    name = x.replace(searchString,replaceString)
                    pm.rename(x,name)
            # if option selected 
            elif selectionOption == 2:
                list = pm.ls(sl=True)
                for x in list:
                    name = x.replace(searchString,replaceString)
                    pm.rename(x,name)
            
        # if before option selected
        
        elif replaceOption == 2:
            # if option hiearchy 
            if selectionOption == 1:
                pm.select(hi=True)
                list = pm.ls(sl=True)
                for x in list:
                    name = replaceString + searchString + x.rpartition(searchString)[2]
                    pm.rename(x,name)
            # if option selected 
            elif selectionOption == 2:
                list = pm.ls(sl=True)
                for x in list:
                    name = replaceString + searchString + x.rpartition(searchString)[2]
                    pm.rename(x,name)
                    
        # if after option selected
        
        elif replaceOption == 3:
            # if option hiearchy 
            if selectionOption == 1:
                pm.select(hi=True)
                list = pm.ls(sl=True)
                for x in list:
                    name = x.rpartition(searchString)[0] + searchString + replaceString
                    pm.rename(x,name)
            # if option selected 
            elif selectionOption == 2:
                list = pm.ls(sl=True)
                for x in list:
                    name = x.rpartition(searchString)[0] + searchString + replaceString
                    pm.rename(x,name)
    def renameChain(self,*args):
        
        selectionList = pm.ls(sl=True)
        i = 0
        for object in selectionList:
            name = object.rpartition('_')[0]
            if name == '':
                print 'empty'
                pm.rename(object,object+'_'+nameIncrements[i]+'_01')
            else:
                pm.rename(object,name+'_'+nameIncrements[i]+'_01')
            i = i + 1
    
    def quit(self,window, *args):
        pm.deleteUI(window)
    def duplicateAlongPath(self,*args):

        '''
        ------------------------------------------

            position along curve

        ------------------------------------------
        '''
        inputX = pm.intField(self.widgets['numberOfDuplicates'],q=True,v=True)
        GOD_object = pm.ls(sl=True)[0]
        curve = pm.textFieldButtonGrp(self.widgets['curvePath'],q=True,tx=True)
        pathLength = pm.arclen(curve,ch=False)
        randomON = pm.checkBox(self.widgets['RandomPathDistance'],q=True,v=True)
        n = 0

        pathIncrement = 1.0 / inputX

        for increment in range(inputX):
            
            object = pm.duplicate(GOD_object,rc=True)
            objGroup = pm.group(object)
            motionPath =      pm.pathAnimation(objGroup,fm=True,f=True,fa='x',ua='y',wut='scene',c=curve)
            pm.delete(pm.listConnections(motionPath+'.uValue'))
            value = rand.uniform(n,(n+pathIncrement))
            if randomON == True:
                pm.setAttr(motionPath+'.uValue',value)
                randomRotate = rand.randint(0,360)

                randomScale = rand.uniform((pm.floatField(self.widgets['randomizeScaleMINPath'],q=True,v=True)),(pm.floatField(self.widgets['randomizeScaleMAXPath'],q=True,v=True)))
                print object
                pm.setAttr(object[0]+'.ry', randomRotate)
                pm.setAttr(object[0]+'.sx', randomScale)
                pm.setAttr(object[0]+'.sy', randomScale)
                pm.setAttr(object[0]+'.sz', randomScale)
            else:
                pm.setAttr(motionPath+'.uValue',n)
            n = n + pathIncrement
            pm.parent(objGroup,'ROOT_enviroment_01')
            


    def instructions(self,*args):

        if pm.window("InstructionsWindow", q=True, exists = True):
            pm.deleteUI("InstructionsWindow")
                        
        InstructionsWindow = pm.window("InstructionsWindow",t="Instructions",w=200,h=300,bgc=[0.15,0.15,0.15], sizeable=False)
        pm.columnLayout(parent = "InstructionsWindow",adjustableColumn=True)
        
        pm.text(l='Instructions', fn='boldLabelFont', align='center' )
        pm.separator(h=10, style = 'none')
        pm.text(l='First define what the prefix of the character rig will be.', align='center' )
        pm.text(l='This is so when rigging multiple characters there are no overlapping names. ', align='center' )
        pm.separator(h=5, style = 'none')
        pm.text(l='Then input how many joints you want in the spine', align='center' )
        pm.text(l='the more joints the smoother the bend but the more weight painting required.', align='center' )
        pm.text(l='Judge based on the topology resolution of your model. ', align='center' )
        pm.separator(h=5, style = 'none')
        pm.text(l='When ready create the "Reference Skeleton" and scale the rig to match your character', align='center' )
        pm.text(l='before placing all the joints based on your model', align='center' )
        pm.separator(h=10, style = 'none')
        pm.text(l='When done press Finalize and your rig will be made! Happy animating!!!', align='center' )
        
        pm.separator(h=20,style='none')
        
        pm.button(l='Exit',c=partial(self.quit, "InstructionsWindow"),h=50,bgc=[0.2,0.2,0.2])
        
        pm.showWindow(InstructionsWindow)
        
        pm.window("InstructionsWindow", e=True,w=500,h=220)

        
    def about(self,*args):
        
        if pm.window("AboutWindow", q=True, exists = True):
            pm.deleteUI("AboutWindow")
            
        aboutWindow = pm.window("AboutWindow",t="About",w=200,h=200,bgc=[0.15,0.15,0.15], sizeable=False)
        pm.columnLayout(parent = "AboutWindow",adj=True)
        
        pm.text(l='About Enviroment Manager', fn='boldLabelFont', align='center' )
        pm.separator(h=10, style = 'none')
        pm.rowColumnLayout(nc=2, cw=[(1,100),(2,190)])
        pm.text(l='Created by:', align='center' )
        pm.text(l='Jeremy Taylor', align='left' )
        pm.separator(h=5, style = 'none')
        pm.separator(h=5, style = 'none')
        pm.text(l='Email:', align='center' )
        pm.text(l='nightsymbol@gmail.com', align='left' )
        pm.separator(h=5, style = 'none')
        pm.separator(h=5, style = 'none')
        pm.text(l='Vimeo Page :', align='center' )
        vimeoLink = pm.text(hl=True, l="https://vimeo.com/spiritforger101", align='left' )
        print vimeoLink
        pm.separator(h=10, style = 'none')
        pm.separator(h=10, style = 'none')
        pm.text(l='Report Bugs:', align='center' )
        pm.text(l='No Link', align='left' )
        
        pm.setParent(u=True)
        
        pm.separator(h=10,style='none')
        
        pm.button(l='Exit',c=partial(self.quit, "AboutWindow"),bgc=[0.2,0.2,0.2])
        
        pm.showWindow(aboutWindow)
        
        pm.window("AboutWindow", e=True,w=290,h=140)

EnviromentManagerWindow()
