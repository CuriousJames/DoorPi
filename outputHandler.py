#!/usr/bin/env python

import time

#
# TODO:
#  set door open time from settings
#

class outputHandler :
    doorRinging=False
    doorbellCount=0
    doorbellOutputs = [
        {
            "name": "doorbell12",
            "inverted": False
        },
        {
            "name": "boorbellCc",
            "inverted": True
        }
    ]
    params = {
        "doorOpenTime": 5,
        "doorbellCcTime": 0.1
    }

    #
    # INITIALISE
    # does what it says on the tin
    #  internalise some things
    #  set initial state of some outputs
    #  get anything useful from settings
    def __init__(self, settings, logger, pi, pinDef) :
        # internalise the stuff
        self.settings = settings
        self.logger = logger
        self.pi = pi
        self.pinDef = pinDef

        # set some outputs
        try :
            pi.write(self.pinDef.pins["doorStrike"],0)
            pi.write(self.pinDef.pins["doorbell12"],0)
            pi.write(self.pinDef.pins["doorbellCc"],0)
            pi.write(self.pinDef.pins["readerLed"],1)
            pi.write(self.pinDef.pins["readerBuzz"],1)
        except :
            self.logger.log("ERRR", "There was an issue setting output pins")

        # get settings
        settingsToGet = ["doorOpenTime", "doorbellCcTime"]
        if self.settings != False :
            for s in settingsToGet :
                try :
                    self.settings["outputHandling"][s]
                except :
                    pass
                else :
                    self.params[s] = self.settings["outputHandling"][s]
                    self.logger.log("INFO", "new setting for output handling", {"parameter": s, "value": self.params[s]} )
            # done
        return

    #
    # open and close the door
    #  this is for when a token has been read and approved
    def openDoor(self):
        # open
        self.setDoor("open")

        # wait
        time.sleep(self.params["doorOpenTime"])

        #Now let's warn that the door is about to close by flashing the Reader's LED
        #l.log("DBUG", "Door Closing soon")
        #i = 5
        #while i < 5:
            #pi.write(p.pins["readerLed"],1)
            #time.sleep(0.1)
            #pi.write(p.pins["readerLed"],0)
            #time.sleep(0.1)
            #i += 1

        # close
        self.setDoor("closed")

        # done
        return


    #
    # set the door to an open or closed state
    #  will do led and strike
    #
    def setDoor(self, state) :
        # error state
        if state != "open" and state != "closed" :
            self.logger.log("WARN", "No state set for changing door state")
            return
        # open
        if state == "open" :
            self.logger.log("DBUG", "Opening door")
            pinState = [{"name": "doorStrike", "state": 1}, {"name": "readerLed", "state": 0}]
        #closed
        if state == "closed" :
            self.logger.log("DBUG", "Closing door")
            pinState = [{"name": "doorStrike", "state": 0}, {"name": "readerLed", "state": 1}]
        # do the pins
        for pin in pinState :
            self.pi.write(self.pinDef.pins[pin["name"]], pin["state"])


    # make the doorbell do a ringing
    def ringDoorbell(self):
        self.doorbellCount+=1
        self.logger.log("DBUG", "******* Bell Count *******", self.doorbellCount)

        if self.doorRinging == False:
            self.doorRinging=True
            self.logger.log("INFO", "Start Doorbell")

            self.doorbellHit()
            self.doorbellHit()
            self.doorbellHit()

            self.doorRinging=False
            self.logger.log("INFO", "Stop Doorbell")

        else:
            self.logger.log("INFO", "NOT Ringing doorbell - it's already ringing")

        return


    def doorbellHit(self) :
        setDoorbellOutState(1)
        time.sleep(2)
        setDoorbellOutState(0)
        time.sleep(0.1)


    def setDoorbellOutState(self, state) :
        if state != 1 and state != 0 :
            return

        for out in self.doorbellOutputs :
            # set state
            newState = state
            # invert if necessary
            if out["inverted"] == True :
                newState ^= 1
            # do the output
            self.pi.write(self.pinDef.pins[out["name"]], newState)
            del newState

        return