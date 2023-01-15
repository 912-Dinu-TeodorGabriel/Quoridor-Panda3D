from distutils.cmd import Command
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import TextNode
from panda3d.core import LVector3, BitMask32
from direct.task.Task import Task
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import DirectButton  
from services import *
import sys



# Now we define some helper functions that we will need later

# This function, given a line (vector plus origin point) and a desired z value,
# will give us the point on the line where the desired z value is what we want.
# This is how we know where to position an object in 3D space based on a 2D mouse
# position. It also assumes that we are dragging in the XY plane.
#
# This is derived from the mathematical of a plane, solved for a given point


class Chessboard(ShowBase):
    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)
        self.services = services()
        self.repo = self.services.repo
        self.repo._read()
        # This code puts the standard title and instruction text on screen
        self.curr_bg = 1
        self.background = OnscreenImage(parent=render2dp, image="models/background1.jpg")
        base.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top)
        self.escapeEvent = OnscreenText(
            text="ESC: Quit", parent=base.a2dTopLeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.1),
            align=TextNode.ALeft, scale = .05)
        self.mouse1Event = OnscreenText(
            text="Left-click and drag: Pick up and drag piece",
            parent=base.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.16), scale=.05)
        self.mouse2Event = OnscreenText(
            text="Left-click on a square: Put a wall",
            parent=base.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.06, -0.22), scale=.05)
        self.mouse3Event = OnscreenImage(
            image="models/walls/wall.png",
            parent=base.a2dTopLeft, pos=(0.14, 0.5, -0.32), scale=.07)
        self.mouse4Event = OnscreenText(
            text="x"+str(self.repo.walls),
            parent=base.a2dTopLeft, align=TextNode.ALeft,
            style=1, fg=(1, 1, 1, 1), pos=(0.25, -0.33), scale=.05)   
        self.mouse5Event = DirectButton(
            image ='models/save.png',
            parent=base.a2dTopLeft, pos=(0.122, 0, -0.48), scale=.05, command = self.repo._write)
        self.mouse6Event = DirectButton(
            image ='models/undo.png',
            parent=base.a2dTopLeft, pos=(0.246, 0, -0.48), scale=.05, command = self.repo.undo)
        self.mouse7Event = DirectButton(
            image ='models/restart.png',
            parent=base.a2dTopLeft, pos=(0.368, 0, -0.48), scale=.05, command = self.repo.restart)
        self.mouse8Event = DirectButton(
            image ='models/image-files.png',
            parent=base.a2dTopLeft, pos=(0.246, 0, -0.63), scale=.05, command = self.bg)    
        self.accept('escape', sys.exit) # Escape quits
        self.disableMouse()  # Disble mouse camera control
        camera.setPosHpr(0, -12, 8, 0, -35, 0)  # Set the camera
        self.setupLights()  # Setup default lighting

        # Since we are using collision detection to do picking, we set it up like
        # any other collision detection system with a traverser and a handler
        self.textObject = OnscreenText(text='', pos=(0.5, -0.8), scale=0.07, fg = (1, 1, 1, 1))
        self.picker = CollisionTraverser()  # Make a traverser
        self.pq = CollisionHandlerQueue()  # Make a handler
        # Make a collision node for our picker ray
        self.pickerNode = CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could separate it
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)
        # self.picker.showCollisions(render)

        # Now we create the chess board and its pieces

        # We will attach all of the squares to their own root. This way we can do the
        # collision pass just on the squares and save the time of checking the rest
        # of the scene

        self.squareRoot = render.attachNewNode("squareRoot")

        # For each square

        for i in range(64):
            # Load, parent, color, and position the model (a single square
            # polygon)
            self.repo.squares[i] = loader.loadModel("models/square")
            self.repo.squares[i].reparentTo(self.squareRoot)
            self.repo.squares[i].setPos(services.SquarePos(i))
            self.repo.squares[i].setColor(WHITE if services.SquareColor(i)  else BLACK)
            # Set the model itself to be collideable with the ray. If this model was
            # any more complex than a single polygon, you should set up a collision
            # sphere around it instead. But for single polygons this works
            # fine.
            self.repo.squares[i].find("**/polygon").node().setIntoCollideMask(
                BitMask32.bit(1))
            # Set a tag on the square's node so we can look up what square this is
            # later during the collision pass
            self.repo.squares[i].find("**/polygon").node().setTag('square', str(i))

            # We will use this variable as a pointer to whatever piece is currently
            # in this square

        # The order of pieces on a chessboard from white's perspective. This list
        # contains the constructor functions for the piece classes defined
        # below
        
        
        # This will represent the index of the currently highlited square
        self.hiSq = False
        # This wil represent the index of the square where currently dragged piece
        # was grabbed from
        self.dragging = False

        # Start the task that handles the picking
        self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept("mouse1", self.grabPiece)  # left-click grabs a piece
        self.accept("mouse1-up", self.releasePiece)  # releasing places it

    def PointAtZ(self, z, point, vec):
        return point + vec * ((z - point.getZ()) / vec.getZ())
    
    def mouseTask(self, task):
        # This task deals with the highlighting and dragging based on the mouse
        if self.repo.winner == False:
            # First, clear the current highlight
            if self.hiSq is not False:
                self.repo.squares[self.hiSq].setColor(services.SquareColor(self.hiSq))
                self.hiSq = False

            # Check to see if we can access the mouse. We need it to do anything
            # else
            if self.mouseWatcherNode.hasMouse():
                # get the mouse position
                mpos = self.mouseWatcherNode.getMouse()

                # Set the position of the ray based on the mouse position
                self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

                # If we are dragging something, set the position of the object
                # to be at the appropriate point over the plane of the board
                if self.dragging is not False:
                    # Gets the point described by pickerRay.getOrigin(), which is relative to
                    # camera, relative instead to render
                    nearPoint = render.getRelativePoint(
                        camera, self.pickerRay.getOrigin())
                    # Same thing with the direction of the ray
                    nearVec = render.getRelativeVector(
                        camera, self.pickerRay.getDirection())
                    self.repo.pieces[self.dragging].obj.setPos(
                        self.PointAtZ(.5, nearPoint, nearVec))

                # Do the actual collision pass (Do it only on the squares for
                # efficiency purposes)
                self.picker.traverse(self.squareRoot)
                if self.pq.getNumEntries() > 0:
                    # if we have hit something, sort the hits so that the closest
                    # is first, and highlight that node
                    self.pq.sortEntries()
                    i = int(self.pq.getEntry(0).getIntoNode().getTag('square'))
                    # Set the highlight on the picked square
                    self.repo.squares[i].setColor(HIGHLIGHT)
                    self.hiSq = i
        else:
            if self.repo.winner == "white":
                self.textObject.setText("Game Over " + "White Wins")
            elif self.repo.winner == 'black':
                self.textObject.setText("Game Over " + "Black Wins")
        return Task.cont

    def grabPiece(self):
        # If a square is highlighted and it has a piece, set it to dragging
        # mode
        if self.hiSq is not False and self.repo.pieces[self.hiSq] and self.repo.pieces[self.hiSq].is_wall == 0 and self.repo.pieces[self.hiSq].obj.getColor() == WHITE:
            self.dragging = self.hiSq
            self.hiSq = False
        elif self.hiSq is not False:
            #put a wall in that square
            if self.repo.pieces[self.hiSq] == None and self.repo.walls and self.repo.recoil_wall_w < 1 and self.repo.winner == False and self.services.check_position(self.hiSq) == False:
                print(self.hiSq)
                self.services.move_white(self.hiSq)
                self.textObject.setText('Great move')
                self.mouse4Event.setText("x" + str(self.repo.walls))
                self.services.move_black()
        else:   
            self.textObject.setText('Illegal move')


    def releasePiece(self):
        # Letting go of a piece. If we are not on a square, return it to its original
        # position. Otherwise, swap it with the piece in the new square
        # Make sure we really are dragging something
        if self.dragging is not False:
            # We have let go of the piece, but we are not on a square
            if self.hiSq is not False and (self.dragging == self.hiSq + 1 or self.dragging == self.hiSq - 1 or self.dragging == self.hiSq + 8 or self.dragging == self.hiSq - 8) and (self.repo.pieces[self.hiSq] == None or self.repo.pieces[self.hiSq].is_wall == 0):
                self.services.move_on_board(self.dragging, self.hiSq)
                self.textObject.setText('Great move')
            else:
                self.textObject.setText('Illegal move')
                self.repo.pieces[self.dragging].obj.setPos(
                    services.SquarePos(self.dragging))
            self.repo.recoil_wall_w = 0
        # We are no longer dragging anything
        self.dragging = False

    def setupLights(self):  # This function sets up some default lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.8, .8, .8, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(LVector3(0, 45, -45))
        directionalLight.setColor((0.2, 0.2, 0.2, 1))
        render.setLight(render.attachNewNode(directionalLight))
        render.setLight(render.attachNewNode(ambientLight))

    def bg(self):
        self.curr_bg += 1
        if self.curr_bg == 5:
            self.curr_bg = 1
        self.background.setImage('models/background'+str(self.curr_bg)+".jpg") # Load an image object
           
def main_gui():
    app = Chessboard()
    app.run()


main_gui()