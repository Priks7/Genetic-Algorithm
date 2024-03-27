from model.Constant import Constant
from model.Reservation import Reservation
from collections import defaultdict


class HtmlOutput:
    ROOM_COLUMN_NUMBER = Constant.DAYS_NUM + 1
    ROOM_ROW_NUMBER = Constant.DAY_HOURS + 1
    COLOR1 = "#319378"
    COLOR2 = "#CE0000"
    CRITERIAS = (' ')
    OK_DESCR = ("Current room has no overlapping", "Current room has enough seats",
                       "Current room with enough computers if they are required",
                       "Professors have no overlapping classes", "Student groups has no overlapping classes")
    FAIL_DESCR = ("Current room has overlapping", "Current room has not enough seats",
                       "Current room with not enough computers if they are required",
                       "Professors have overlapping classes", "Student groups has overlapping classes")
    PERIODS = (
    "", "9 - 10 AM", "10 - 11 AM", "11 - 12 AM", "12 - 1 PM", "1 - 2 PM", "2 - 3 PM", "3 - 4 PM", "4 - 5 PM", "5 - 6 PM", "6 - 7 PM",
    "7 - 8 PM", "8 - 9 PM")
    WEEK_DAYS = ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY")

    @staticmethod
    def getCourseClass(cc, criterias, ci):
        COLOR1 = HtmlOutput.COLOR1
        COLOR2 = HtmlOutput.COLOR2
        CRITERIAS = HtmlOutput.CRITERIAS
        length_CRITERIAS = len(CRITERIAS)

        sb = [cc.Course.Name, "<br />", "<span style='color: red;'>", cc.Professor.Name, "</span>", "<br />", "/".join(map(lambda grp: grp.Name, cc.Groups)), "<br />"]
        if cc.LabRequired:
            sb.append("Lab<br />")

        for i in range(length_CRITERIAS):
            sb.append("<span style='color: green")
            if criterias[ci + i]:
                sb.append(COLOR1)
                sb.append("' title='")
                sb.append(HtmlOutput.OK_DESCR[i])
            else:
                sb.append(COLOR2)
                sb.append("' title='")
                sb.append(HtmlOutput.FAIL_DESCR[i])
            sb.append("'> ")
            sb.append(CRITERIAS[i])
            sb.append(" </span>")

        return sb

    @staticmethod
    def generateTimeTable(solution, slot_table):
        ci = 0

        time_table = defaultdict(list)
        items = solution.classes.items        
        ROOM_COLUMN_NUMBER = HtmlOutput.ROOM_COLUMN_NUMBER
        getCourseClass = HtmlOutput.getCourseClass

        for cc, reservation_index in items():
            reservation = Reservation.parse(reservation_index)

            # coordinate of time-space slot
            dayId = reservation.Day + 1
            periodId = reservation.Time + 1
            roomId = reservation.Room
            dur = cc.Duration

            key = (periodId, roomId)
            if key in slot_table:
                room_duration = slot_table[key]
            else:
                room_duration = ROOM_COLUMN_NUMBER * [0]
                slot_table[key] = room_duration
            room_duration[dayId] = dur

            for m in range(1, dur):
                next_key = (periodId + m, roomId)
                if next_key not in slot_table:
                    slot_table[next_key] = ROOM_COLUMN_NUMBER * [0]
                if slot_table[next_key][dayId] < 1:
                    slot_table[next_key][dayId] = -1

            if key in time_table:
                room_schedule = time_table[key]
            else:
                room_schedule = ROOM_COLUMN_NUMBER * [None]
                time_table[key] = room_schedule

            room_schedule[dayId] = "".join(getCourseClass(cc, solution.criteria, ci))
            ci += len(HtmlOutput.CRITERIAS)

        return time_table

    @staticmethod
    def getHtmlCell(content, rowspan):
        if rowspan == 0:
            return "<td></td>"

        if content is None:
            return ""

        sb = []
        if rowspan > 1:
            sb.append("<td style='border: .1em solid black; padding: .25em' rowspan='")
            sb.append(rowspan)
            sb.append("'>")
        else:
            sb.append("<td style='border: .1em solid black; padding: .25em'>")

        sb.append(content)
        sb.append("</td>")
        return "".join(str(v) for v in sb)

    @staticmethod
    def getResult(solution):
        configuration = solution.configuration
        nr = configuration.numberOfRooms
        getRoomById = configuration.getRoomById

        slot_table = defaultdict(list)
        time_table = HtmlOutput.generateTimeTable(solution, slot_table)  # Tuple[0] = time, Tuple[1] = roomId
        if not slot_table or not time_table:
            return ""

        sb = []
        sb.append("<h1 style='text-align: center; color: #000;'> Data Science Time-Table - AIT Pune</h1>\n")

        for roomId in range(nr):
            room = getRoomById(roomId)
            for periodId in range(HtmlOutput.ROOM_ROW_NUMBER):
                if periodId == 0:
                    sb.append("<div id='room_")
                    sb.append(room.Name)
                    sb.append("' style='padding: 0.5em'>\n")
                    sb.append("<table style='border-collapse: collapse; width: 95%'>\n")
                    sb.append(HtmlOutput.getTableHeader(room))
                else:
                    key = (periodId, roomId)
                    room_duration = slot_table[key] if key in slot_table.keys() else None
                    room_schedule = time_table[key] if key in time_table.keys() else None
                    sb.append("<tr>")
                    for dayId in range(HtmlOutput.ROOM_COLUMN_NUMBER):
                        if dayId == 0:
                            sb.append("<th style='border: .1em solid black; padding: .25em' scope='row' colspan='2'>")
                            sb.append(HtmlOutput.PERIODS[periodId])
                            sb.append("</th>\n")
                            continue

                        if room_schedule is None and room_duration is None:
                            continue

                        content = room_schedule[dayId] if room_schedule is not None else None
                        sb.append(HtmlOutput.getHtmlCell(content, room_duration[dayId]))
                    sb.append("</tr>\n")

                if periodId == HtmlOutput.ROOM_ROW_NUMBER - 1:
                    sb.append("</table>\n</div>\n")

        return "".join(str(v) for v in sb)

    @staticmethod
    def getTableHeader(room):
        sb = ["<tr><th style='border: .1em solid black; color: blue;' scope='col' colspan='2'>Room: ", room.Name, "</th>\n"]
        for weekDay in HtmlOutput.WEEK_DAYS:
            sb.append("<th style='border: .1em solid black; padding: .25em; width: 15%' scope='col' rowspan='2'>")
            sb.append(weekDay)
            sb.append("</th>\n")
        sb.append("</tr>\n")
        sb.append("<tr>\n")
        sb.append("<th style='border: .1em solid black; padding: .25em'>Lab: ")
        sb.append("Yes" if room.Lab else "No")
        sb.append("</th>\n")
        sb.append("<th style='border: .1em solid black; padding: .25em'>Seats: ")
        sb.append(room.NumberOfSeats)
        sb.append("</th>\n")
        sb.append("</tr>\n")
        return "".join(str(v) for v in sb)
