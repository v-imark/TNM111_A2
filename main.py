import pandas as pd
import tkinter as tk
import numpy

data1 = pd.read_csv('data1.csv', header=None)
data2 = pd.read_csv('data2.csv', header=None)


class Gui:
    def __init__(self, master, d1, d2):
        self.master = master
        self.data1 = d1
        self.data2 = d2
        self.xRange = 0
        self.yRange = 0
        self.nTicks = 0
        self.xTickLength = 0
        self.yTickLength = 0
        self.dataTitle = 'Dataset 1'
        self.buttonIds = []
        self.labels = []
        self.data = self.initData(d1)
        self.yMax = 560
        self.xMax = 760
        self.xMin = 40
        self.yMin = 40
        self.x_origin = 400
        self.y_origin = 300

        self.quadColors = ['#b04ce6', '#db4ce6', '#e64cb5', '#e64c82', '#f0ec16']
        self.baseColor = '#2e1dc2'
        self.selectColors = ['#c2231d', '#1dc223']

        self.canvas = tk.Canvas(self.master)
        self.drawGraph([0, 0], [0, 0])
        self.canvas.pack(fill=tk.BOTH, expand=1)

    def initData(self, data):
        data_xmax = max(data[0])
        data_xmin = min(data[0])
        self.xRange = max(abs(data_xmin), abs(data_xmax)) * 2 * 1.1

        data_ymax = max(data[1])
        data_ymin = min(data[1])
        self.yRange = max(abs(data_ymin), abs(data_ymax)) * 2 * 1.1

        self.nTicks = 10
        self.xTickLength = self.xRange / 10
        self.yTickLength = self.yRange / 10
        data['neighbors'] = 'l'
        dist = [0 for i in range(len(data))]

        for i, row in data.iterrows():
            for j, inner_row in data.iterrows():
                a = numpy.array((row[0], row[1]))
                b = numpy.array((inner_row[0], inner_row[1]))
                dist[j] = numpy.linalg.norm(a - b)

            res = sorted(range(len(dist)), key=lambda sub: dist[sub])[1:6]
            data.loc[i, 'neighbors'] = ','.join([str(elem) for elem in res])
        self.buttonIds = [0 for i in range(len(data))]
        self.labels = data[2].unique()

        return data

    def changeData(self, dataset):
        self.canvas.delete("all")
        if dataset == 1:
            self.data = self.initData(self.data1)
        if dataset == 2:
            self.data = self.initData(self.data2)

        self.dataTitle = 'Dataset ' + str(dataset)
        self.drawGraph([0, 0], [0, 0])

    def drawDataButton(self):
        dataset = 1
        if self.dataTitle == 'Dataset 1':
            dataset = 2
        button1 = tk.Button(self.canvas, width=15, height=4, text='Change Dataset', command=lambda: self.changeData(dataset))
        button1.place(x=820, y=460)

    def drawTicks(self):
        xLength = (self.xMax - 40) / self.nTicks
        yLength = (self.yMax - 40) / self.nTicks
        x = self.x_origin
        y = self.y_origin
        for i in range(1, int(self.nTicks / 2) + 1):
            self.canvas.create_line(x + xLength * i, y - 4, x + xLength * i, y + 4)
            self.canvas.create_line(x - 4, y - yLength * i, x + 4, y - yLength * i)
            self.canvas.create_line(x - xLength * i, y - 4, x - xLength * i, y + 4)
            self.canvas.create_line(x - 4, y + yLength * i, x + 4, y + yLength * i)

    def drawTickLabels(self, offsetX, offsetY):
        xLength = (self.xMax - 40) / self.nTicks
        yLength = (self.yMax - 40) / self.nTicks
        x = self.x_origin
        y = self.y_origin
        for i in range(1, int(self.nTicks / 2) + 1):
            self.canvas.create_text(x + xLength * i, y + 10, text=round(self.xTickLength * i + offsetX, 2))
            self.canvas.create_text(x - xLength * i, y + 10, text=round(-self.xTickLength * i + offsetX, 2))
            self.canvas.create_text(x - 18, y - yLength * i, text=round(self.yTickLength * i + offsetY, 2))
            self.canvas.create_text(x - 18, y + yLength * i, text=round(-self.yTickLength * i + offsetY, 2))

    def drawPoints(self, offsetX, offsetY):
        for i, r in self.data.iterrows():
            x, y = self.getCanvasCoords(r[0], r[1])
            if r[2] == self.labels[0]:
                self.buttonIds[i] = self.drawTri(x, y, i, offsetX, offsetY)
            elif r[2] == self.labels[1]:
                self.buttonIds[i] = self.drawCircle(x, y, i, offsetX, offsetY)
            elif r[2] == self.labels[2]:
                self.buttonIds[i] = self.drawRect(x, y, i, offsetX, offsetY)

    def onRightPointClick(self, event, neighbors, index):
        if self.canvas.itemcget(self.buttonIds[index], 'fill') == self.selectColors[0]:
            self.resetColors()
            return
        self.resetColors()
        self.canvas.itemconfig(self.buttonIds[index], fill=self.selectColors[0])
        indices = neighbors.split(',')
        for i in indices:
            tag = self.buttonIds[int(i)]
            self.canvas.itemconfig(tag, fill=self.selectColors[1])

    def getCanvasCoords(self, x, y):
        xScaleFactor = (self.xMax - self.xMin) / self.xRange
        xPos = x * xScaleFactor + self.x_origin
        yScaleFactor = (self.yMax - self.yMin) / self.yRange
        yPos = -y * yScaleFactor + self.y_origin
        return xPos, yPos

    def drawCircle(self, x, y, index, offsetX, offsetY):
        circleId = self.canvas.create_oval(x - 5 + offsetX, y - 5 + offsetY, x + 5 + offsetX, y + 5 + offsetY,
                                           fill=self.baseColor)
        self.canvas.tag_bind(circleId, '<Button-3>',
                             lambda e: self.onRightPointClick(e, self.data.loc[index, 'neighbors'], index))
        self.canvas.tag_bind(circleId, '<Button-1>',
                             lambda e: self.movePoints(e, index))
        return circleId

    def drawRect(self, x, y, index, offsetX, offsetY):
        rectId = self.canvas.create_rectangle(x - 4 + offsetX, y - 4 + offsetY, x + 4 + offsetX, y + 4 + offsetY,
                                              fill=self.baseColor)
        self.canvas.tag_bind(rectId, '<Button-3>',
                             lambda e: self.onRightPointClick(e, self.data.loc[index, 'neighbors'], index))
        self.canvas.tag_bind(rectId, '<Button-1>',
                             lambda e: self.movePoints(e, index))
        return rectId

    def drawTri(self, x, y, index, offsetX, offsetY):
        points = [x + offsetX, y - 6 + offsetY, x + 6 + offsetX, y + 6 + offsetY, x - 6 + offsetX, y + 6 + offsetY]
        triId = self.canvas.create_polygon(points, fill=self.baseColor, outline='black')
        self.canvas.tag_bind(triId, '<Button-3>',
                             lambda e: self.onRightPointClick(e, self.data.loc[index, 'neighbors'], index))
        self.canvas.tag_bind(triId, '<Button-1>',
                             lambda e: self.movePoints(e, index))
        return triId

    def resetColors(self):
        for tag in self.buttonIds:
            self.canvas.itemconfig(tag, fill=self.baseColor)

    def drawAxes(self):
        self.canvas.create_line(self.xMin, self.y_origin, self.xMax, self.y_origin)
        self.canvas.create_line(self.x_origin, self.yMin, self.x_origin, self.yMax)

    def movePoints(self, event, index):
        if self.canvas.itemcget(self.buttonIds[index], 'fill') == self.quadColors[4]:
            self.canvas.delete("all")
            self.drawGraph([0, 0], [0, 0])
            return

        self.canvas.delete("all")
        moveX, moveY = self.getCanvasCoords(self.data.loc[index, 0], self.data.loc[index, 1])
        moveX = self.x_origin - moveX
        moveY = self.y_origin - moveY
        self.drawGraph([moveX, moveY], [-self.data.loc[index, 0], -self.data.loc[index, 1]])
        self.quadrantColor(index)

    def quadrantColor(self, index):
        originX = self.data.loc[index, 0]
        originY = self.data.loc[index, 1]
        for i in range(len(self.buttonIds)):
            if self.data.loc[i, 0] < originX:
                self.canvas.itemconfig(self.buttonIds[i], fill=self.quadColors[0])
                if self.data.loc[i, 1] < originY:
                    self.canvas.itemconfig(self.buttonIds[i], fill=self.quadColors[1])
            if self.data.loc[i, 0] >= originX:
                self.canvas.itemconfig(self.buttonIds[i], fill=self.quadColors[2])
                if self.data.loc[i, 1] > originY:
                    self.canvas.itemconfig(self.buttonIds[i], fill=self.quadColors[3])

        self.canvas.itemconfig(self.buttonIds[index], fill=self.quadColors[4])

    def drawGraph(self, pointOffset, tickOffset):
        self.drawAxes()
        self.drawTicks()
        self.drawTickLabels(tickOffset[0], tickOffset[1])
        self.drawPoints(pointOffset[0], pointOffset[1])
        self.drawLegend()
        self.drawDataButton()

    def drawLegend(self):
        self.canvas.create_rectangle(800, 40, 960, 560, fill='#e8e8e8', outline='black')
        self.canvas.create_text(880, 60, text=self.dataTitle, font=('Helvetica', '24', 'bold'))
        x = 830
        y = 100

        textOffset = 20
        offset = 40
        self.canvas.create_polygon([x, y - 6, x + 6, y + 6, x - 6, y + 6], fill=self.baseColor, outline='black')
        self.canvas.create_text(x + textOffset, y, text=self.labels[0])
        self.canvas.create_rectangle(x - 4 + offset, y - 4, x + 4 + offset, y + 4, fill=self.baseColor)
        self.canvas.create_text(x + textOffset + offset, y, text=self.labels[1])
        self.canvas.create_oval(x - 5 + offset * 2, y - 5, x + 5 + offset * 2, y + 5, fill=self.baseColor)
        self.canvas.create_text(x + textOffset + offset * 2, y, text=self.labels[2])

        x = 820
        textOffset = 10
        yOffset = 40
        xOffset = 30
        barLength = 20
        self.canvas.create_text(x + (barLength + xOffset * 3) / 2, y + yOffset - textOffset * 1.2,
                                text='Quadrant Colors')

        self.canvas.create_rectangle(x, y - 4 + yOffset, x + barLength, y + 4 + yOffset, fill=self.quadColors[3])
        self.canvas.create_text(x + textOffset, y + yOffset + textOffset * 1.2, text='Q1')
        self.canvas.create_rectangle(x + xOffset, y - 4 + yOffset, x + xOffset + barLength, y + 4 + yOffset,
                                     fill=self.quadColors[0])
        self.canvas.create_text(x + textOffset + xOffset, y + yOffset + textOffset * 1.2, text='Q2')
        self.canvas.create_rectangle(x + xOffset * 2, y - 4 + yOffset, x + xOffset * 2 + barLength, y + 4 + yOffset,
                                     fill=self.quadColors[1])
        self.canvas.create_text(x + textOffset + xOffset * 2, y + yOffset + textOffset * 1.2, text='Q3')
        self.canvas.create_rectangle(x + xOffset * 3, y - 4 + yOffset, x + xOffset * 3 + barLength, y + 4 + yOffset,
                                     fill=self.quadColors[2])
        self.canvas.create_text(x + textOffset + xOffset * 3, y + yOffset + textOffset * 1.2, text='Q4')

        self.canvas.create_rectangle(x, y - 4 + yOffset * 2, x + barLength + xOffset * 3, y + 4 + yOffset * 2,
                                     fill=self.quadColors[4])
        self.canvas.create_text(x + (barLength + xOffset * 3) / 2, y + yOffset * 2 + textOffset * 1.2,
                                text='Selected (Left-Click)')

        self.canvas.create_rectangle(x, y - 4 + yOffset * 3, x + barLength + xOffset * 3, y + 4 + yOffset * 3,
                                     fill=self.selectColors[0])
        self.canvas.create_text(x + (barLength + xOffset * 3) / 2, y + yOffset * 3 + textOffset * 1.2,
                                text='Selected (Right-Click)')

        self.canvas.create_rectangle(x, y - 4 + yOffset * 4, x + barLength + xOffset * 3, y + 4 + yOffset * 4,
                                     fill=self.selectColors[1])
        self.canvas.create_text(x + (barLength + xOffset * 3) / 2, y + yOffset * 4 + textOffset * 1.2, text='Neighbors')


root = tk.Tk()
root.geometry("1000x600")
gui = Gui(root, data1, data2)
root.mainloop()
