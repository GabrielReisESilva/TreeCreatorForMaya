from maya import cmds
import libs.vector as v2
import random
import math

TREE_HEIGHT = 5.0
DO_SLEEP = False

class Tree(object):


    def __init__(self):
        self.treeTransform = None
        self.trunkTransform = None
        self.leafMaterial0 = self.CreateNewLambert([0.00,1.00,0.00], "leaf_material0")
        self.leafMaterial1 = self.CreateNewLambert([0.00,0.50,0.00], "leaf_material1")
        self.leafMaterial2 = self.CreateNewLambert([0.00,0.80,0.00], "leaf_material2")
        self.trunkMaterial = self.CreateNewLambert([0.15,0.03,0.00], "trunk_material")

    def CreateMultiple(self, x=1, z=1):
        park = cmds.group(em=True)
        for i in range(0, x):
            for j in range(0, z):
                self.CreateRandomTree(i * 4, j * 4)
        cmds.rename(park, 'Park#')

    def CreateTree(self, minRadius, maxRadius, minHeight, maxHeight, branches, leafColor0, leafColor1, leafColor2, branchColor, name='Tree#', deltaX=0, deltaZ=0):
        radius = round(random.uniform(minRadius, maxRadius), 3)
        height = round(random.uniform(minHeight, maxHeight), 3)
        subdivisionHeight1 = round(random.uniform(0.05, 0.2), 3) * height
        subdivisionHeight2 = subdivisionHeight1 + round(random.uniform(0.3, 0.5), 3) * height
        subdivisionDelta1 = self.GetDelta(0, math.pi/2.0, 0, 0.3)
        subdivisionDelta2 = [x + y for x, y in zip(subdivisionDelta1, self.GetDelta(0, math.pi/2.0, 0, 0.8))]
        self.leafMaterial0 = self.CreateNewLambert(leafColor0, "leaf_material0")
        self.leafMaterial1 = self.CreateNewLambert(leafColor1, "leaf_material1")
        self.leafMaterial2 = self.CreateNewLambert(leafColor2, "leaf_material2")
        self.trunkMaterial = self.CreateNewLambert(branchColor, "trunk_material")

        #CREATING TREE
        self.trunkTransform = self.CreateTrunk(radius, height, subdivisionHeight1, subdivisionHeight2, subdivisionDelta1, subdivisionDelta2, 0.7, 0.7)
        self.treeTransform = self.trunkTransform

        #CREATING BRANCHES
        for i in range(0, branches):
            branchesType = random.randrange(0, 3);
            if branchesType == 1:
                branch1 = self.CreateBranch(radius, height, subdivisionHeight1, subdivisionHeight2, subdivisionDelta1, subdivisionDelta2, 0.7, 0.6, 1)
                self.treeTransform = cmds.group(self.treeTransform, branch1)
            if branchesType == 2:
                branch2 = self.CreateBranch(radius, height, subdivisionHeight1, subdivisionHeight2, subdivisionDelta1, subdivisionDelta2, 0.7, 0.5, 3)
                self.treeTransform = cmds.group(self.treeTransform, branch2)

        #CREATING LEAVES
        leaves = self.CreateLeaves(height-0.3, 1.3, 1.8)
        self.treeTransform = cmds.group(self.treeTransform, leaves)

        #TRANSFORM TREE
        cmds.setAttr(self.treeTransform+".translateX", deltaX)
        cmds.setAttr(self.treeTransform+".translateZ", deltaZ)
        cmds.setAttr(self.treeTransform+".rotateY", random.randrange(0, 360))

        #cmds.rename(self.treeTransform, name)
        return cmds.rename(self.treeTransform, name)

    def CreateRandomTree(self, name='Tree#', deltaX=0, deltaZ=0):
        return self.CreateTree(0.5, 1.5, 4.0, 7.5, 4, [0.0,1.0,0.0], [0.0,0.75,0.0], [0.0,0.5,0.0], [0.15,0.03,0.0], name, deltaX, deltaZ)

    def CreateTrunk(self, radius, height, subdivisionHeight1, subdivisionHeight2, subdivisionDelta1, subdivisionDelta2, sd1Scale, sd2Scale):
        cmds.softSelect(sse=0)
        trunkTransform, trunkConstructor = cmds.polyCylinder(r = radius, h = height, sx = 8, sy = 1, sz = 1, ax = (0,1,0), ch = True)
        cmds.sets(trunkTransform, e=True, forceElement=self.trunkMaterial)

        #MOVE TO CENTER
        cmds.move(0, height * 0.5, 0, trunkTransform, a = True)

        #SCALE DOWN TOP VERTICES
        cmds.select(clear=True)
        for vertex in range(8,16):
            cmds.select('%s.vtx[%s]' % (trunkTransform, vertex), add=True)
        cmds.scale(0.2, 0.2, 0.2, p = (0, height, 0))

        #MAKE TRUNK SUB-DIVISIONS
        cmds.select(trunkTransform)
        cmds.polyCut(pc = [0, subdivisionHeight1, 0], ro = [90,0,0], ef = True, eo = [0,0,0])
        cmds.select(trunkTransform)
        cmds.polyCut(pc = [0, subdivisionHeight2, 0], ro = [90,0,0], ef = True, eo = [0,0,0])

        #TRANSFORM SUBDIVIONS
        cmds.select(clear=True)
        for vertex in range(18,34):
            cmds.select('%s.vtx[%s]' % (trunkTransform, vertex), add=True)
        cmds.move(subdivisionDelta1[0], subdivisionDelta1[1], subdivisionDelta1[2], r = True)
        cmds.scale(sd1Scale, sd1Scale, sd1Scale, r = True)
        #cmds.rotate(subdivisionDelta1[2] * 30, subdivisionDelta1[1], -subdivisionDelta1[0] * 30, r = True, os = True)

        cmds.select(clear=True)
        for vertex in range(34,50):
            cmds.select('%s.vtx[%s]' % (trunkTransform, vertex), add=True)
        cmds.move(subdivisionDelta2[0], subdivisionDelta2[1], subdivisionDelta2[2], r = True)
        cmds.scale(sd2Scale, sd2Scale, sd2Scale, r = True)
        #cmds.rotate(-subdivisionDelta2[2] * 30, subdivisionDelta2[1], subdivisionDelta2[0] * 30, r = True, os = True)

        #SCALE UP BOTTOM VERTICES
        cmds.select(clear=True)
        for vertex in range(0,8):
            cmds.select('%s.vtx[%s]' % (trunkTransform, vertex), add=True)
        cmds.scale(1.4, 1.4, 1.4, p = (0, 0, 0))

        return trunkTransform

    def CreateBranch(self, radius, height, subdivisionHeight1, subdivisionHeight2, subdivisionDelta1, subdivisionDelta2, branchScale1, branchScale2, branch):
        cmds.softSelect(sse=0)
        trunkTransform, trunkConstructor = cmds.polyCylinder(r = radius, h = height, sx = 8, sy = 1, sz = 1, ax = (0,1,0), ch = True)
        cmds.sets(trunkTransform, e=True, forceElement=self.trunkMaterial)

        #MOVE TO CENTER
        cmds.move(0, height * 0.5, 0, trunkTransform, a = True)

        #SCALE DOWN TOP VERTICES
        cmds.select(clear=True)
        for vertex in range(8,16):
            cmds.select('%s.vtx[%s]' % (trunkTransform, vertex), add=True)
        cmds.scale(0.25, 0.25, 0.25, p = (0, height, 0))

        #MAKE TRUNK SUB-DIVISIONS
        cmds.select(trunkTransform)
        cmds.polyCut(pc = [0, subdivisionHeight1, 0], ro = [90,0,0], ef = True, eo = [0,0,0])
        cmds.select(trunkTransform)
        cmds.polyCut(pc = [0, subdivisionHeight2, 0], ro = [90,0,0], ef = True, eo = [0,0,0])

        #TRANSFORM SUBDIVIONS
        branchScale = branchScale1
        cmds.select(clear=True)
        for vertex in range(18, 34):
            cmds.select('%s.vtx[%s]' % (trunkTransform, vertex), add=True)
        cmds.move(subdivisionDelta1[0], subdivisionDelta1[1], subdivisionDelta1[2], r = True)
        cmds.scale(branchScale, branchScale, branchScale, r = True)

        if branch == 1:
            subdivisionDelta2 = [x + y for x, y in zip(subdivisionDelta1, self.GetDelta(math.pi/2.0, 2*math.pi, 1.0, 2.0))]

        branchScale = branchScale2

        cmds.select(clear=True)
        for vertex in range(34, 50):
            cmds.select('%s.vtx[%s]' % (trunkTransform, vertex), add=True)
        cmds.move(subdivisionDelta2[0], subdivisionDelta2[1], subdivisionDelta2[2], r = True)
        cmds.scale(branchScale, branchScale, branchScale, r = True)
        #cmds.rotate(-subdivisionDelta2[2] * 30, subdivisionDelta2[1], subdivisionDelta2[0] * 30, r = True, os = True)

        #MOVE TOP
        topDelta = []
        if branch == 1:
            topDelta = self.GetDelta(0.0, 2 * math.pi, 0.0, 1.0)
            topDelta[1] = round(random.uniform(-0.1, 1.5), 3)
        else:
            topDelta = self.GetDelta(0.0, 2 * math.pi, 1.0, 2.5)
            topDelta[1] = round(random.uniform(0.5, 2.0), 3)

        topDelta = [x + y for x, y in zip(subdivisionDelta2, topDelta)]

        cmds.select(clear=True)
        for vertex in range(8,16) + range(17,18):
            cmds.select('%s.vtx[%s]' % (trunkTransform, vertex), add=True)
        cmds.move(topDelta[0], topDelta[1], topDelta[2], r = True)
        cmds.scale(0.6, 0.6, 0.6, r = True)

        #Remove bottom part
        cmds.select(clear=True)
        for face in range(0,16):
            cmds.select('%s.f[%s]' % (trunkTransform, face), add=True)
        if branch == 3:
            for face in range(24, 32):
                cmds.select('%s.f[%s]' % (trunkTransform, face), add=True)
        cmds.delete()

        return trunkTransform

    def CreateLeaves(self, height, minSize, maxSize):
        leafBase = cmds.polyPrimitive( r=1, l=1, pt=0)[0]
        cmds.move(height, y = True)
        cmds.polyChipOff(dup=False, kft=False)
        cmds.polyChipOff(dup=False, kft=True, ltz = 0.08, ran = 1.0)
        cmds.polyExtrudeFacet(ltz = 0.6)
        cmds.polySmooth()
        cmds.polySeparate()

        cmds.xform(cp = True)

        for leaf in cmds.ls(sl=True):
            leafScale = round(random.uniform(minSize, maxSize), 3)
            cmds.select(leaf)
            cmds.polySoftEdge(a=0, name=leaf)
            cmds.scale(leafScale, leafScale, leafScale)
            leafPosition = cmds.xform(leaf, q=True, rp=True, ws=True)
            leafPosition[1] = height + 0.5 * (height - leafPosition[1])
            cmds.xform(leaf, t=leafPosition, ws=True)
            self.SetRandomLeafColor(leaf)

        return leafBase

    def CreateBushes(self, posX = 0, posZ = 0):
        brushesBase = cmds.polyPrimitive(r=0.4, pt=0)[0]
        cmds.polyChipOff(dup=False, kft=False)
        cmds.polyChipOff(dup=False, kft=True, ltz = 0.1, ran = 1.0)
        cmds.polyExtrudeFacet(ltz = 0.2)
        cmds.polySmooth()
        cmds.polySeparate()

        cmds.xform(cp = True)

        for leaf in cmds.ls(sl=True):
            leafScale = round(random.uniform(2, 2.5), 3)
            cmds.select(leaf)
            cmds.polySoftEdge(a=0, name=leaf)
            cmds.scale(leafScale, leafScale, leafScale)
            leafPosition = cmds.xform(leaf, q=True, rp=True, ws=True)
            if leafPosition[1] < 0:
                cmds.delete(leaf)
            else:
                cmds.xform(leaf, t=leafPosition, ws=True)
                self.SetRandomLeafColor(leaf)

        cmds.setAttr(brushesBase+".translateX", posX)
        cmds.setAttr(brushesBase+".translateZ", posZ)

        return cmds.rename(brushesBase, 'Bushes#')

    def GetDelta(self, minAngle, maxAngle, minRadius, maxRadius):
        angle = round(random.uniform(minAngle, maxAngle), 4)
        radius = round(random.uniform(minRadius, maxRadius), 3)
        return [radius * math.sin(angle), 0.0, radius * math.cos(angle)]

    def SetRandomLeafColor(self, node):
        colorIndex = random.randrange(0, 3)
        if colorIndex == 0:
            cmds.sets(node, e=True, forceElement=self.leafMaterial0)
        if colorIndex == 1:
            cmds.sets(node, e=True, forceElement=self.leafMaterial1)
        if colorIndex == 2:
            cmds.sets(node, e=True, forceElement=self.leafMaterial2)

    def CreateNewLambert(self, color, name = 'NewLambert'):
        if cmds.objExists(name) == False:
            cmds.shadingNode('lambert', asShader=True, n=name)
            cmds.sets(r=True, noSurfaceShader=True, em=True, n='%sSG' % name)
            cmds.connectAttr('%s.outColor' % name, '%sSG.surfaceShader' % name)

        cmds.setAttr('%s.color' % name, color[0], color[1], color[2], typ='double3')
        return '%sSG' % name
        #cmds.sets(node, e=True, forceElement='%sSG' % name)

    def CreatePark(self, width, length, treesDist, bushesDist, createTree = None):
        if createTree is None:
            createTree = lambda x, y: self.CreateRandomTree('ParkTree#', x, y)

        groundMaterial = self.CreateNewLambert([0.31,0.55,0.0], 'ground_material')
        ground = cmds.polyPlane(w = width*1.5, h = length*1.5, sx = width/1, sy = length/1, name = 'Park')[0]
        cmds.sets(ground, e=True, forceElement=groundMaterial)

        distToAttempts = width * length / 100
        treeAttempts = treesDist * distToAttempts
        bushesAttempts = bushesDist * distToAttempts
        positions = []
        while treeAttempts > 0 or bushesAttempts > 0:
            if treeAttempts > 0:
                pos = v2.Vector.random([width, length])
                if not self.IsCloseTo(pos, positions, 3):
                    cmds.parent(createTree(pos.x-width/2.0, pos.y-length/2.0), ground)
                    positions.append(pos)
            if bushesAttempts > 0:
                pos = v2.Vector.random([width, length])
                if not self.IsCloseTo(pos, positions, 2):
                    cmds.parent(self.CreateBushes(pos.x-width/2.0, pos.y-length/2.0), ground)
                    positions.append(pos)

            treeAttempts -= 1
            bushesAttempts -= 1

    def IsCloseTo(self, position, positions, maxDistance):
        for pos in positions:
            if v2.Vector.distance(pos, position) < maxDistance:
                return True

        return False