# import data types
# from ..utilities import dataTypes
# from enum import Enum

########################
# Enum definitions
########################
# class Season(Enum):
#     fall = False
#     winter = False
#     spring = False


########################
# Class definitions
########################
class CourseTuple:
    def __init__(self, numRequired = 0, courses = [], courseTuples = []):
        self.numRequired = numRequired
        self.courses = courses
        self.courseTuples = courseTuples

class Course:
    def __init__(self, subject = "", number = "", title = "", units = 0, preReqs = CourseTuple(), coReqs = CourseTuple(), concurrentReqs = [], seasonsOffered = {"fall": False, "winter": False, "spring": False}, numChildren = 0, parents = [], numParents = 0, totalChildren = 0):
        self.subject = subject
        self.number = number
        self.title = title
        self.units = units
        self.preReqs = preReqs
        self.coReqs = coReqs
        self.concurrentReqs = concurrentReqs
        self.seasonsOffered = seasonsOffered # default to false
        self.numChildren = numChildren
        self.parents = parents
        self.numParents = numParents
        self.totalChildren = totalChildren
    def hasChildren(self):
        if len(self.preReqs) > 0 or len(self.coReqs) > 0:
            return True
        else:
            return False

class Quarter:
    def __init__(self, courses = [], season = ""):
        self.courses = courses
        self.season = season
    # get total num of units in quarter
    def getUnits(self):
        n = 0
        for course in self.courses:
            n += course.units
        return n
            
class CoursePlan:
    # @param completed is an array of completed courses (or equivalent)
    def __init__(self, quarters = [], completed = [], maxUnits = 0):
        assert all(isinstance(quarter, Quarter) for quarter in quarters)
        self.quarters = quarters
        self.completed = completed
        self.maxUnits = maxUnits
    # get # of filled quarters
    def getNumQuarters(self):
        return len(self.quarters)
    def isCompleted(self, course):
        for completedCourse in self.completed:
            completedId = completedCourse.subject + completedCourse.number
            courseId = course.subject + course.number
            if completedId == courseId:
                return True
        return False




########################
# Function definitions
########################

# used for checking pre-reqs AND co-reqs
# return true if course is in plan, checking up until quarter [endIndex]
# @param offset is the number of quarters from the end of the plan at which it stops searching
def courseInPlan(course, plan, offset):
    # inspect every quarter in plan
    for i in range(0, len(plan.quarters)-offset):
        # inspect every course in quarter
        for prevCourse in plan.quarters[i].courses:
            idPrevCourse = prevCourse.subject + prevCourse.number
            idCourse = course.subject + course.number
            if idPrevCourse == idCourse:
                return True
    return False

# return true if the course tuple is satisfied, given the current plan and offset (quarters from the current quarter to cut the check sort)
def satisfied(plan, courseTuple, offset):
    if courseTuple.numRequired == 0:
        return True
    numSatisfied = 0
    for course in courseTuple.courses:
        if plan.isCompleted(course) or courseInPlan(course, plan, offset):
            numSatisfied += 1
        if numSatisfied >= courseTuple.numRequired:
            return True
    for nestedTuple in courseTuple.courseTuples:
        if satisfied(plan, nestedTuple, offset):
            numSatisfied += 1
        if numSatisfied >= courseTuple.numRequired:
            return True
    return False

# print out a single course plan
def printCoursePlan(plan):
    assert isinstance(plan, CoursePlan)
    print("Plan:")
    for i in range(len(plan.quarters)):
        print(" Qtr " + str(i + 1) + ", " + str(plan.quarters[i].getUnits()) + " unit(s)")
        for course in plan.quarters[i].courses:
            print(" -" + course.subject + str(course.number))



# Evaluation of an individual course, for whether or not it passes the constraints
def courseEval(newCourse, currentPlan, maxUnits, currentQuarter, concurrentCourse):
    # confirm correct type
    assert isinstance(newCourse, Course)
    assert isinstance(currentPlan, CoursePlan)
    assert type(maxUnits) == int
    assert type(currentQuarter) == int

    # 1. course already placed in plan?
    if courseInPlan(newCourse, currentPlan, 0):
        print("New course has already been placed.")
        return False

    # 2. is it offered this quarter?
    currentSeason = currentPlan.quarters[currentQuarter].season
    if not newCourse.seasonsOffered[currentSeason]:
        print("New course is not offered this quarter.")
        return False

    # 3. All pre-reqs satisfied? 
    # @param offset=1 b/c checking pre-reqs so must be 1 qtr back
    print("Checking if preReqs satisfied for " + newCourse.subject + newCourse.number)
    if not satisfied(currentPlan, newCourse.preReqs, 1):
        return False

    # 4. All co-reqs satisfied? 
    # @param offset=0 b/c checking co-reqs so course can be in current quarter. This works b/c coReqs in the A1 tree are listed as dependent on the courses that they satisfy so the breadth first search will pull them out first and then they will be in the plan (if they worked) prior to checking if the course that can use it as a co-req works.
    print("Checking if coReqs satisfied for " + newCourse.subject + newCourse.number)
    if not satisfied(currentPlan, newCourse.coReqs, 0):
        return False

    totalUnits = currentPlan.quarters[currentQuarter].getUnits()

    # 5. Determine if there's a concurrent-req and sum units for newCourse and/(or not and) concurrent course
    if len(newCourse.concurrentReqs) > 0:
        # add to total units that of the two concurrent-req courses
        units = newCourse.concurrentReqs[0].units + newCourse.units
        totalUnits += units
        concurrentCourse["id"] = newCourse.concurrentReqs[0].subject + newCourse.concurrentReqs[0].number
    else:
        # add just the units of the og course
        totalUnits += newCourse.units

    # 6. Check if exceeded max num of units
    if totalUnits > currentPlan.maxUnits:
        return False

    # At very end if none of the conditions fail
    return True


# @param a1 is the required coursework to create a plan for
def createCoursePlan(a1):
    # 1. get a1 as top level ANDed single-dim array, and where it only contains ANDed pre-reqs
    # assert isinstance(a1, CourseTuple) 
    # 2. Count number of children (pre/co) for each course in A1
    for course in a1:
        for preReq in course.preReqs.courses:
            course.numChildren += 1
        for coReq in course.coReqs.courses:
            course.numChildren += 1

    # 3. Sort A1 from least to most reqs (children) with bubblesort (quicksort is adv.)
    for i in range(len(a1)):
        for j in range(len(a1)-1-i):
            if a1[j].numChildren > a1[j+1].numChildren:
                a1[j], a1[j+1] = a1[j+1], a1[j]

    print("Ordered courses")
    for course in a1:
        print("-" + course.subject + course.number)

    # 4/5. Foreach course in A1, starting after 0 children
    for course in a1:
        if course.numChildren > 0:
            # point all child pre-reqs to their parents
            for child in course.preReqs.courses:
                if not course in child.parents:
                    child.parents.append(course)
                    child.numParents += 1

            # point all child co-reqs to their parents
            for child in course.coReqs.courses:
                if not (course in child.parents):
                    child.parents.append(course)
                    child.numParents += 1

    for course in a1:
        print(course.subject + course.number + "'s parents are")
        for parent in course.parents:
            print("  ->" + parent.subject + parent.number)

    # 6. Now since all children are mapped to their parents, remove courses from the top level of A1 that have parents
    # 7. Recursively sort by # of children (pre and co) from least to most.
    # 8. BFS on A1 starting at imaginary root course. Push element elements in a stack as they appear (as S1)
    # Course passes eval?
    # 9. Pop course off of the stack (S1) and insert into the course plan. Remove course from each of its parents in the A1
    # 10. Perform 7-9 for every quarter until all courses from A1 have been assigned quarters that work
    

    
    


########################
# Main
########################
def main():
    # init/create data structures
    # prev taken coursework
    completedCourses = [Course("MATH", "21")];
    courses = [
            [Course("AMS", "10", "Applied Bullshit", 5), Course("PHYS", "5A", "Intro to Cuntimatics", 5), Course("PHYS", "5L", "Intro to Cuntimatics, Lab", 1)], 
            [Course("AMS", "20", "Applied Bullshit", 5), Course("PHYS", "5B", "Intro to Cuntimatics", 5), Course("PHYS", "5M", "Intro to Cuntimatics, Lab", 2)]
            ]
    quarters = [Quarter(courses[0], "fall"), Quarter(courses[1], "winter"), Quarter([Course("CMPE", "16")], "spring")]
    plan = CoursePlan(quarters, completedCourses, 19)

    # preReq tuple
    p5c = CourseTuple(2, [], [CourseTuple(2, [courses[0][1], courses[1][1]], []), CourseTuple(1, [courses[0][2], courses[1][2]], [])])
    c5c = CourseTuple(2, [Course("CMPE", "16"), courses[0][0]], [])
    concurrent = [Course("PHYS", "5N")]


    # print plan
    printCoursePlan(plan);

    # define course for testing
    newCourse = Course("PHYS", "5C", "Intro to Cuntimatics", 5, p5c, c5c, concurrent, {"fall":False, "winter":True, "spring":True})

    # courseEval unit test 
    concurrentCourse = {"id": ""}
    if courseEval(newCourse, plan, 19, 2, concurrentCourse):
        # check if concurrent course was added
        if concurrentCourse["id"]:
            # add the concurrent course by its unique id (look up in the dictionary)
            print("Course eval succeeded. And added conccurent course " + concurrentCourse["id"] + ".")
        else:
            print("Course eval succeeded.")
    else:
        print("Course eval failed.")


    # courses[0][0].preReqs = CourseTuple(1, [courses[1][1], courses[0][1], courses[0][1]],[])
    # courses[1][0].preReqs  = CourseTuple(1, [courses[1][1], courses[0][1]], [])
    
    cmpe16 = Course("CMPE", "16")
    cmpe16.preReqs = CourseTuple(1, [], [])

    cmpe17 = Course("CMPE", "17")
    cmpe17.preReqs = CourseTuple(1, [cmpe16], [])

    cmpe18 = Course("CMPE", "18")
    cmpe18.preReqs = CourseTuple(1, [cmpe17], [])

    cmpe19 = Course("CMPE", "19")
    cmpe19.preReqs = CourseTuple(1, [cmpe16, cmpe18], [])

    cmpe20 = Course("CMPE", "20")
    cmpe20.preReqs = CourseTuple(1, [cmpe16, cmpe17, cmpe18, cmpe19], [])

    math24 = Course("MATH", "24")
    math24.preReqs = CourseTuple(1, [], [])

    a1 = [cmpe16, cmpe17, cmpe18, cmpe19, cmpe20, math24]
    createCoursePlan(a1)
    




main()
