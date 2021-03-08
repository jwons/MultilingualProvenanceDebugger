class DebugRecord:

    def __init__(self, userChoice, programInfo, userAnnotation):
        self._userChoice = userChoice
        self._programInfo = programInfo
        self._userAnnotation = userAnnotation

    def prettyPrint(self):
        print(f"Debug action: {self._userChoice}")
        print("Program state:\n")
        print(self._programInfo)
        if self._userAnnotation is not None:
            print(f"Annotation: {self._userAnnotation}")
    
    def printProgramFrame(self):
        program_lines = self._programInfo.splitlines()
        max_line_length = max([len(line) for line in program_lines])
        frame = "=" * max_line_length
        print(frame)
        print(self._programInfo)
        print(frame)

    def setAnnotation(self, annotation):
        self._userAnnotation = annotation

    def writeDict(self):
        asDict = {}
        asDict["userAction"] = self._userChoice
        asDict["programInfo"] = self._programInfo
        asDict["userAnnotation"] = self._userAnnotation
        return asDict

    @staticmethod
    def fromDict(contentDict):
        return DebugRecord(contentDict["userAction"], contentDict["programInfo"], contentDict["userAnnotation"])
