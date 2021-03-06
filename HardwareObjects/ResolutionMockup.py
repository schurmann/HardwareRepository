from HardwareRepository import BaseHardwareObjects
import logging
import math


class ResolutionMockup(BaseHardwareObjects.Equipment):
    def _init(self):
        self.connect("equipmentReady", self.equipmentReady)
        self.connect("equipmentNotReady", self.equipmentNotReady)

        return BaseHardwareObjects.Equipment._init(self)

    def init(self):
        self.currentResolution = 3
        self.detmState = None
        self.state = 2
        self.dtox = self.getObjectByRole("dtox")
        self.energy = self.getObjectByRole("energy")
        self.detector = self.getObjectByRole("detector")
        self.connect(self.dtox, "positionChanged", self.dtoxPositionChanged)
        self.dtox.move(self.res2dist(self.currentResolution))

        # Default value detector radius - corresponds to Eiger 16M:
        self.det_radius = 155.625
        detector = self.detector
        if detector is not None:
            # Calculate detector radius
            px = float(detector.getProperty('px', default_value=0))
            py = float(detector.getProperty('py', default_value=0))
            width = float(detector.getProperty('width', default_value=0))
            height = float(detector.getProperty('height', default_value=0))
            det_radius = 0.5 * min(px * width, py * height)
            if det_radius > 0:
                self.det_radius = det_radius

    def beam_centre_updated(self, beam_pos_dict):
        pass

    def dtoxPositionChanged(self, pos):
        self.newResolution(self.dist2res(pos))

    def getWavelength(self):
        return self.energy.getCurrentWavelength()

    def wavelengthChanged(self, pos=None):
        self.recalculateResolution(pos)

    def energyChanged(self, energy):
        self.wavelengthChanged(12.3984 / energy)

    def res2dist(self, res=None):

        if res is None:
            res = self.currentResolution

        try:
            ttheta = 2 * math.asin(self.getWavelength() / (2 * res))
            return self.det_radius / math.tan(ttheta)
        except:
            return None

    def dist2res(self, dist=None):
        if dist is None:
            logging.getLogger('HWR').error(
                "Refusing to calculate resolution from distance 'None'"
            )
            return
        try:
            ttheta = math.atan(self.det_radius / dist)
            if ttheta != 0:
                return self.getWavelength() / (2 * math.sin(ttheta / 2))
        except:
            logging.getLogger().exception("error while calculating resolution")
            return None

    def recalculateResolution(self):
        self.currentResolution = self.dist2res(self.dtox.getPosition())

    def equipmentReady(self):
        self.emit("deviceReady")

    def equipmentNotReady(self):
        self.emit("deviceNotReady")

    def getPosition(self):
        if self.currentResolution is None:
            self.recalculateResolution()
        return self.currentResolution

    def get_value(self):
        return self.getPosition()

    def newResolution(self, res):
        if res:
            self.currentResolution = res
            self.emit("positionChanged", (res, ))
            self.emit('valueChanged', (res, ))

    def getState(self):
        return self.state

    def connectNotify(self, signal):
        pass

    def detmStateChanged(self, state):
        pass

    def detmPositionChanged(self, pos):
        pass

    def getLimits(self, callback=None, error_callback=None):
        return (0, 20)

    def move(self, pos, wait=True):
        self.dtox.move(self.res2dist(pos), wait=wait)

    def motorIsMoving(self):
        return self.dtox.motorIsMoving() or self.energy.moving

    def newDistance(self, dist):
        pass

    def stop(self):
        self.dtox.stop()
