from django.http import HttpResponse
from django.shortcuts import render
from ga.models import Attribute, Indicator, Assessment, AssessmentMethod, Program, Course, SemesterLU, AYEAR_CHOICES, SEASON_CHOICES
import xlsxwriter
import math

# Takes y,x coords and returns excel cell ID
def toLetters(y, x):
    x += 1
    result = '$'
    while x > 0:
        m = x % 26
        x //= 26
        result = chr(64 + m) + result
    result += '$' + str(y+1)
    return result


def slice_data(years):
    print(years)
    # list of years as pair of terms (A, W)
    terms = [
        SemesterLU.objects.filter(year=y, term='A') |
        SemesterLU.objects.filter(year=str(int(y)+1),term='W')
        for y in years 
    ]
    
    attributes = set([])
    indicators = set([])
    methods = set([])
    assessments = set([])
    
    for term in terms:
    
        # list of assessments in that year
        ass = set(Assessment.objects.filter(
            semester__in=term
        ))
        assessments |= ass
        print(ass)
        
        # list of assessment methods in that year
        ams = set([a.assessmentMethod for a in assessments])
        methods |= ams
        
        # list of indicators in that year
        inds = set([am.indicator for am in ams])
        indicators |= inds
        
        # list of attributes in that year
        atts = set([ind.attribute for ind in inds])
        attributes |= atts
        
        return list(attributes), list(indicators), list(methods), list(assessments)
    
    return slices
    


#def export(yearsWanted,prog):
def export(yearsWanted,prog):

    #yearsWanted = ['2000','2001']
    #programs = Program.objects.all()
    #prog = programs[0]

    # get querysets
    attributes, indicators, assessMethods, assessments = slice_data(yearsWanted)
    print(attributes, indicators, assessMethods, assessments)
    
    # get attributes
    #attributes = Attribute.objects.all()

    numOfAttribs = len(attributes)
    numOfYears = len(yearsWanted)

    # filename
    file_name = 'GAMS_'+prog.name+ '_'+yearsWanted[0]+'-'+str((int(yearsWanted[-1]))+1)+'.xlsx'

    # init workbook
    
    response = HttpResponse(content_type='application/vdn.ms-excel')
    response['Content-Disposition'] = 'attachment;filename="'+file_name+'"'
    
    workbook = xlsxwriter.Workbook(response, {'in_memory' : True})

    # Define format for headers
    headerFormat = workbook.add_format()
    headerFormat.set_font_size(10)
    headerFormat.set_align('center')
    headerFormat.set_align('vcenter')
    headerFormat.set_bold()
    headerFormat.set_text_wrap()
    headerFormat.set_bg_color('gray')
    headerFormat.set_border(1)

    # Define format for data
    dataFormat = workbook.add_format()
    dataFormat.set_font_size(10)
    dataFormat.set_align('center')
    dataFormat.set_align('vcenter')
    dataFormat.set_text_wrap()
    dataFormat.set_border(1)

    # overview x and y values
    aX = 0
    aY = 3
    dX = 1
    dY = 1

    # chart indexing
    cX_offset = 8
    cY_offset = 17
    cX = 0
    cY = numOfAttribs + 5


    # worksheet for overview (All)
    wsAll = workbook.add_worksheet('All')

    # headers for overview
    wsAll.set_column('A:A',12)   
    wsAll.merge_range('A1:A3', 'Graduate Attributes', headerFormat)
 

    # overview headers
    for yearW in yearsWanted:
      wsAll.merge_range(dY,dX,dY,dX+1,yearW + '-' + str(int(yearW)+1), headerFormat)
      wsAll.write(dY+1,dX,'Avg', headerFormat)
      wsAll.write(dY+1,dX+1,'σ', headerFormat)
      dX += 2
    wsAll.merge_range(0,1,0,dX-1,'Results', headerFormat)

    dX += 2
    dY = 1
    x_offset = dX
    for yearW in yearsWanted:
      wsAll.merge_range(dY,dX,dY,dX+1,yearW + '-' + str(int(yearW)+1), headerFormat)
      wsAll.merge_range(dY+1,dX,dY+1,dX+1,'Avg', headerFormat)
      dX += 2
    wsAll.merge_range(0,x_offset,0,dX-1,'Results', headerFormat)

    dX = 1
    dY = 3

    # divide into attributes
    for attrib in attributes:

        # each attribute has its chart in the overview
        attribChart = workbook.add_chart({'type':'line'})
        attribChart.set_x_axis({'name':'Assessment Methods'})
        attribChart.set_y_axis({'name':'Assessment','min':0,'max':5,'minor_unit':0,'major_unit':1})
        attribChart.set_title({'name': attrib.code + '-' + attrib.name})
        attribChart.set_chartarea({'border':{'color':'black'}})

        # write attributes into overview
        wsAll.write(aY,aX,attrib.code, dataFormat)
        aY += 1

        # set dX back to beginning of line
        dX = 1

        # worksheet for each attribute (data)
        ws = workbook.add_worksheet(attrib.code)

        # Row/column sizes for headers
        ws.set_row(0,25)
        ws.set_row(1,25)
        ws.set_row(2,25)
        ws.set_column('A:B', 12)
        ws.set_column('C:C', 35)
        ws.set_column('D:F', 10)
        ws.set_column('G:I', 12)


        # Headers Content
        ws.merge_range('A1:A2', '', headerFormat)
        ws.merge_range('B1:C2', attrib.code + ' ' + attrib.name, headerFormat)
        ws.merge_range('D1:F2', 'Courses', headerFormat)
        ws.write('A3', 'Assessment Code', headerFormat)
        ws.write('B3', 'Related (sub)attribute', headerFormat)
        ws.write('C3', 'Indicator', headerFormat)
        ws.write('D3', 'Introduced', headerFormat)
        ws.write('E3', 'Taught', headerFormat)
        ws.write('F3', 'Used', headerFormat)
        ws.merge_range('G1:G3', 'Course in which assessment made', headerFormat)
        ws.merge_range('H1:H3', 'Method of assessment', headerFormat)
        ws.merge_range('I1:I3', 'Time of asessment', headerFormat)

        
        # worksheet indexes (data)
        x = 0
        y = 3        

        # list of indicators for attribute
        #indicators = Indicator.objects.filter(attribute=attrib,programs__in=[prog])
       
        for indic in indicators:
            
            # filter indicators
            if indic.attribute != attrib or prog not in indic.programs.all():
              continue 
            
            # list of assessmentMethods for this indicator
            #assessMethods = AssessmentMethod.objects.filter(indicator=indic)

            # write assessment code, course assessed and time of assessment
            i = 0
            for method in assessMethods:
            
                # filter methods
                if method.indicator != indic:
                  continue
            
                x = 0
                # assessment codes
                ws.write(y,x,method.indicator.code + '-' + str(i+1), dataFormat)              
                x = 6
                # course assessed
                ws.write(y,x,method.course.code, dataFormat)
                x= 7
                # eval medium
                ws.write(y,x,method.assessment_medium, dataFormat)
                x = 8
                # time of assessment
                ws.write(y,x,method.time_semester + ' of ' + method.time_year + 'th year', dataFormat)
                # indicator (merged)
                x = 2
                if i == 0:
                    ws.write(y,x,indic.description, dataFormat)
                else:
                    ws.merge_range(y-i,x,y,x,indic.description, dataFormat)
                # introduced
                x = 3
                courses = indic.introduced.all()
                s = ''
                for c in courses:
                    s = s + ' ' + c.code
                if i == 0:
                    ws.write(y,x,s, dataFormat)
                else:
                    ws.merge_range(y-i,x,y,x,s, dataFormat)  
                # taught
                x = 4
                courses = indic.taught.all()
                s = ''
                for c in courses:
                    s = s + ' ' + c.code
                if i == 0:
                    ws.write(y,x,s, dataFormat)
                else:
                    ws.merge_range(y-i,x,y,x,s, dataFormat) 
                # utilized
                x = 5
                courses = indic.used.all()
                s = ''
                for c in courses:
                    s = s + ' ' + c.code
                if i == 0:
                    ws.write(y,x,s, dataFormat)
                else:
                    ws.merge_range(y-i,x,y,x,s, dataFormat) 
                i = i+1
                y = y+1                
        
        #x = 0    
        #ws.merge_range(y,x,y,x+8,'end of indicators', dataFormat)

        x = 9
        y = 0

        # for each year...
        for yearW in yearsWanted:

          attribAvg = 0
          attribDev = 0
          indicNoEvals = 0
        
          # results header
          ws.set_column(x,x+3, 4)
          ws.set_column(x+4,x+4, 6)
          ws.set_column(x+5,x+5, 4)
          ws.set_column(x+6,x+7, 6)
          ws.set_column(x+8,x+8, 4)
          ws.set_column(x+9,x+10, 6)

          ws.merge_range(y,x,y,x+10, 'Year ' + yearW + '-' + str(int(yearW)+1), headerFormat)
          ws.merge_range(y+1,x,y+1,x+4, 'Results', headerFormat)
          ws.merge_range(y+1,x+5,y+1,x+7, 'Assessment', headerFormat)
          ws.merge_range(y+1,x+8,y+1,x+10, 'Indicator', headerFormat)
          ws.write(y+2,x, '1', headerFormat)
          ws.write(y+2,x+1, '2', headerFormat)
          ws.write(y+2,x+2, '3', headerFormat)
          ws.write(y+2,x+3, '4', headerFormat)
          ws.write(y+2,x+4, 'Sample', headerFormat)
          ws.write(y+2,x+5, 'w', headerFormat)
          ws.write(y+2,x+6, 'Avg', headerFormat)
          ws.write(y+2,x+7, 'σ', headerFormat)
          ws.write(y+2,x+8, 'w', headerFormat)
          ws.write(y+2,x+9, 'Avg', headerFormat)
          ws.write(y+2,x+10, 'σ', headerFormat)

          y = y + 3

          # list of semesters associated to year wanted
          autumnSemester = SemesterLU.objects.filter(year=yearW,term='A')
          winterSemester = SemesterLU.objects.filter(year=str(int(yearW)+1),term='W')
          semesters = autumnSemester | winterSemester          

          for indic in indicators:
          
            # filter indicators
            if indic.attribute != attrib or prog not in indic.programs.all():
              continue 
              
            #assessMethods = AssessmentMethod.objects.filter(indicator=indic)
            
            indicOnes = 0
            indicTwos = 0
            indicThrees = 0
            indicFours = 0
            indicTotalNum = 0
            indicAvg = 0
            indicDev = 0

            i = 0
            
            for method in assessMethods:
              
              # filter methods
              if method.indicator != indic:
                continue
              
              #assessments = Assessment.objects.filter(assessmentMethod=method,semester__in=semesters)
              
              ones = 0
              twos = 0
              threes = 0
              fours = 0
              totalNum = 0
              avg = 0
              dev = 0
              
              for assess in assessments:
              
                # filter assessments
                if assess.assessmentMethod != method or assess.semester not in semesters:
                  continue
              
                # count number of 1s
                if(assess.numOf1 != None):
                  ones += assess.numOf1
                  indicOnes += assess.numOf1
                # count number of 2s
                if(assess.numOf2 != None):
                  twos += assess.numOf2
                  indicTwos += assess.numOf2
                # count number of 3s
                if(assess.numOf3 != None):
                  threes += assess.numOf3
                  indicThrees += assess.numOf3
                # count number of 4s
                if(assess.numOf4 != None):
                  fours += assess.numOf4
                  indicFours += assess.numOf4
		
              # write number of 1s
              ws.write(y,x,ones, dataFormat)
              # write number of 2s
              ws.write(y,x+1,twos, dataFormat)
              # write number of 3s
              ws.write(y,x+2,threes, dataFormat)
              # write number of 4s
              ws.write(y,x+3,fours, dataFormat)
              # write sample size
              totalNum = ones + twos + threes + fours
              indicTotalNum += totalNum
              ws.write(y,x+4, totalNum, dataFormat)

              # write weight for assessments. Weight is 1
              ws.write(y,x+5,1,dataFormat)
              # write average for assessments  
              if(totalNum != 0):
                avg = (1*ones + 2*twos + 3*threes + 4*fours)/totalNum
              else:
                avg = 0
              ws.write(y,x+6, avg, dataFormat)
              # write standard deviation for assessments
              if(totalNum != 0):
                dev = math.sqrt((ones*math.pow(math.fabs(avg - 1),2) + twos*math.pow(math.fabs(avg - 2),2) + threes*math.pow(math.fabs(avg - 3),2) + fours*math.pow(math.fabs(avg - 4) ,2))/totalNum)               
              else:
                dev = 0
              ws.write(y,x+7, dev, dataFormat)

              # write weight for indicator. Weight is 1
              if i == 0:
                ws.write(y,x+8,1, dataFormat)
              else:
                ws.merge_range(y-i,x+8,y,x+8,1, dataFormat)
              # write average for indicator
              if (indicTotalNum != 0):
                indicAvg = (1*indicOnes + 2*indicTwos + 3*indicThrees + 4*indicFours)/indicTotalNum
              else:
                indicAvg = 0
              if i == 0:
                ws.write(y,x+9,indicAvg, dataFormat)
              else:
                ws.merge_range(y-i,x+9,y,x+9,indicAvg, dataFormat)
              # write standard deviation for indicator
              if (indicTotalNum != 0):
                indicDev = math.sqrt((indicOnes*math.pow(math.fabs(indicAvg - 1),2) + indicTwos*math.pow(math.fabs(indicAvg - 2),2) + indicThrees*math.pow(math.fabs(indicAvg - 3),2) + indicFours*math.pow(math.fabs(indicAvg - 4) ,2))/indicTotalNum)  
              else:
                indicDev = 0
              if i == 0:
                ws.write(y,x+10,indicDev, dataFormat)
              else:
                ws.merge_range(y-i,x+10,y,x+10,indicDev, dataFormat)
                              
              i = i + 1
              y = y + 1

            # adjust attribute values
            attribAvg += indicAvg
            attribDev += indicDev
            # do not count non-evals
            if(indicAvg == 0):
                indicNoEvals += 1

          dividor = len(indicators) - indicNoEvals
          if(dividor != 0):
            attribAvg /= dividor
            attribDev /= dividor
          else:
            attribAvg = 0
            attribDev = 0

          # write attribute totals for year
          ws.merge_range(y,x+5,y,x+8,'Attribute total', headerFormat)
          ws.write(y,x+9,attribAvg, headerFormat)
          ws.write(y,x+10,attribDev, headerFormat)
          wsAll.write(dY,dX,attribAvg, dataFormat)
          wsAll.merge_range(dY,dX+2+numOfYears*2,dY,dX+3+numOfYears*2, attribAvg, dataFormat)
          dX += 1
          wsAll.write(dY,dX,attribDev, dataFormat)

          y = 0
          x += 11
          dX += 1

          # add assessment totals to attribute chart
          attribChart.add_series({
            'categories': [attrib.code,3,0,3+len(assessMethods)-1,0],
            'values': [attrib.code,y+3,x-5,y+3+len(assessMethods)-1,x-5],
            'marker': {'type':'diamond'},
            'name': yearW + '-' + str(int(yearW)+1)
          })

        # end of year
        
        wsAll.insert_chart(cY,cX,attribChart)
        cY += cY_offset
        dY += 1        
      #end of attribute    

    # Global chart by attribute
    if(numOfAttribs > 0):
      byAttribChart = workbook.add_chart({'type':'line'})
      dX = 1
      dY = 3
      for year in yearsWanted:
        byAttribChart.add_series({
          'categories': ['All',3,0,3+numOfAttribs-1,0],
          'values': ['All',3,dX,3+numOfAttribs-1,dX],
          'marker': {'type':'diamond'},
          'name': year + '-' + str(int(year)+1)
        })
        dX += 2

        byAttribChart.set_x_axis({'name':'Attributes'})
        byAttribChart.set_y_axis({'name':'Assessment','min':0,'max':5,'minor_unit':0,'major_unit':1})
        byAttribChart.set_title({'name':'Results by attribute'})
        byAttribChart.set_chartarea({'border':{'color':'black'}})
        wsAll.insert_chart(cY,cX,byAttribChart)

    cY += cY_offset

    # Global charts by year (3 attributes per chart)  
    if(numOfAttribs > 0):
      dX = 1 + 2 + numOfYears*2
      dY = 3
      attributeChunks = [attributes[x:x+3] for x in range(0,numOfAttribs,3)]  
      for chunk in attributeChunks:
        byYearChart = workbook.add_chart({'type':'line'})
        for attrib in chunk:       
          byYearChart.add_series({
            'categories': ['All',1,1,1,numOfYears*2],
            'values': ['All',dY,dX,dY,dX+(numOfYears*2)-1],
            'marker': {'type':'diamond'},
            'name': attrib.code
          })
          dY += 1
        byYearChart.set_x_axis({'name':'Year'})
        byYearChart.set_y_axis({'name':'Assessment','min':0,'max':5,'minor_unit':0,'major_unit':1})
        byYearChart.set_title({'name':'Results by year (attributes ' + chunk[0].code + '-' + chunk[-1].code + ')'})
        byYearChart.set_chartarea({'border':{'color':'black'}})
        wsAll.insert_chart(cY,cX,byYearChart)
        cY += cY_offset
        
    # rubric stuff
    for attrib in attributes:

      # worsheet for each attribute (rubric)
      wsR = workbook.add_worksheet(attrib.code + 'tools')

      wsR.set_column('A:A', 18)
      wsR.set_column('B:F', 25)

      wsR.write(0,0,'Rubrics for ' + attrib.name, dataFormat)
      wsR.write(2,0,'Assessment Code', headerFormat)
      wsR.write(2,1,'Criteria', headerFormat)
      wsR.write(2,2,'Exceeds Expectations - 4', headerFormat)
      wsR.write(2,3,'Meets Expectations - 3', headerFormat)
      wsR.write(2,4,'Needs Improvement - 2', headerFormat)
      wsR.write(2,5,'Unacceptable - 1', headerFormat)

      # worksheet indexes (rubric)
      rX = 0
      rY = 3
    
      # list of indicators for attribute
      #indicators = Indicator.objects.filter(attribute=attrib,programs__in=[prog])
      for indic in indicators:
      
        # filter indicators
        if indic.attribute != attrib or prog not in indic.programs.all():
          continue   
      
        # list of assessmentMethods for this indicator
        #assessMethods = AssessmentMethod.objects.filter(indicator=indic)
        i = 0
        for method in assessMethods:
         
          if method.indicator != indic:
            continue
         
          rX = 0
          wsR.write(rY,rX,method.indicator.code + '-' + str(i+1), dataFormat)
          rX += 1
          wsR.write(rY,rX,method.criteria, dataFormat)
          rX += 1
          wsR.write(rY,rX,method.expectation4, dataFormat)
          rX += 1
          wsR.write(rY,rX,method.expectation3, dataFormat)
          rX += 1
          wsR.write(rY,rX,method.expectation2, dataFormat)
          rX += 1
          wsR.write(rY,rX,method.expectation1, dataFormat)
          i = i+1
          rY = rY+1
      
    workbook.close()

    # xlsx code end



    return response
    #return HttpResponse("<h1> Exported excel")
