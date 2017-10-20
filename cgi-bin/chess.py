#! /usr/bin/python

print 'Content-Type: text/html\n'
import copy

import cgi
import cgitb
cgitb.enable()
urldata = cgi.FieldStorage()


#location is (a-h)(1-8) i.e. d5
#d5 is used in all commented examples


########## GLOBALS ##########

columns = ['a','b','c','d','e','f','g','h']
rows = ['1','2','3','4','5','6','7','8']

data = {}

#constructing data
def dataformat(team,newgame=False):
    l = []
    if newgame == True:
        for line in open(team+'def.txt').readlines():
            l.append(line.strip().split(','))
    else:
        for line in open(team+'data.txt').readlines():
            l.append(line.strip().split(','))
    data[team] = l

#test cases:

#king cannot move out of the check from the rook at b6 and move into the single check in a1 although a1 is not in the original double check
#data = {'B':[['king','b1']],
        #'W':[['king','h8'],
             #['rook','b6'],
             #['rook','g1']]}
#gen_moveset('king','b1','B') should be ['a2,'c2']

#similar to the last case but the king can move out of the check by killing the vertical check
#data = {'B':[['king','b1']],
        #'W':[['king','h8'],
             #['rook','b2'],
             #['rook','g1']]}
#gen_moveset('king','b1','B') should be ['b2']

#piece (knight at d5) not being able to move and therefore cause a check (what we call a "fool's check"
#data = {'B':[['king','a5'],
             #['knight','d5']],
        #'W':[['king','h8'],
             #['rook','g5']]}
#gen_moveset('knight','d5','B') should be []

#piece (queen at c3) not being able to kill a check if it means causing another
#data = {'B':[['king','a5'],
             #['queen','c3']],
        #'W':[['king','h8'],
             #['rook','c5'],
             #['bishop','d2']]}
#gen_moveset('queen','c3','B') should be []

#not walking into a check by killing another
#data = {'B':[['king','a5']],
        #'W':[['king','h8'],
             #['rook','a6'],
             #['rook','d6']]}
#gen_moveset('king','a5','B') should be ['b4','b5']

#stalemate
#data = {'B':[['king','a1']],
        #'W':[['king','a3'],
             #['rook','b3']]}

#kings "attacking" each other
#data = {'B':[['king','b5']],
        #'W':[['king','d5']]}
#just to make sure they can't kill themselves


splitdata = {'B':{},
             'W':{}}
#location:piece
def compile_splitdata():
    for team in data:
        for piece in data[team]:
            splitdata[team][piece[1]] = piece[0]


########## RANDOM HELPFUL FUNCTIONS ##########
def remove_multiples(l):
    returnlist = []
    for item in l:
        if item not in returnlist:
            returnlist.append(item)
    return returnlist

def get_king_location(team):
    s = ''
    for piece in data[team]:
        if piece[0] == 'king':
            #the king's location
            kinglocation = piece[1]
    return kinglocation

########## DATA RETRIEVAL FUNCTIONS ##########
locations = {'B':[],
             'W':[]}

def compile_locations():
    for team in data:
        for piece in data[team]:
            locations[team].append(piece[1])

paths = {'B':[],
         'W':[]}

def compile_paths():
    for team in data:
        allpaths = []
        for piece in data[team]:
            allpaths+=gen_moveset(piece[0],piece[1],team,locations,'yes','yes')
            #false check declared to prevent crash
        returnedpaths = remove_multiples(allpaths)
        returnedpaths.sort()
        paths[team] = returnedpaths

pieces = {'B':[],
          'W':[]}

def compile_pieces():
    for team in data:
        for piece in data[team]:
            pieces[team].append(piece[0])




locationswithoutking = {'B':[],
                        'W':[]}
checkpaths = {'B':[],
              'W':[]}
#when the king is in check, he cannot move into the path of an enemy piece
#i.e. a king is at b1 and two rooks are attacking from b6 and g1
#if the king moves to a1, he will still be in the way of the g1 rook
#by creating a path dictionary with no king, all moves like this can be accounted for and therefore avoided
def compile_locationswithoutking():
    for team in data:
        for piece in data[team]:
            if piece[0] != 'king':
                locationswithoutking[team].append(piece[1])
            
def compile_checkpaths():
    for team in data:
        allcheckpaths = []
        for piece in data[team]:
            if piece[0] != 'king':
                allcheckpaths+=gen_moveset(piece[0],piece[1],team,locationswithoutking,'yes')
                #it's still a false check declaration
        returnedcheckpaths = remove_multiples(allcheckpaths)
        returnedcheckpaths.sort()
        checkpaths[team] = returnedcheckpaths


########## CASTLING ##########

castles = {'B' : [],#['right','yes'],
                    #['left', 'yes'],
                    #['king','yes']],
           'W' : []}#['right','yes'],
                    #['left', 'yes'],
                    #['king','yes']]}

def castleformat(team,newgame=False):
    l = []
    if newgame == True:
        for line in open('defcastle.txt').readlines():
            l.append(line.strip().split(','))
    else:
        for line in open(team+'castles.txt').readlines():
            l.append(line.strip().split(','))
    castles[team] = l
    
########## CHECK(MATE)/STALEMATE ##########   
def is_check(team,locs=locations,pths=paths,checkpths=checkpaths,pieceran='notking'):
    #'team variable is the team being attacked
    if team == 'B':
        otherteam = 'W'
    else:
        otherteam = 'B'
        
    #Check:
        #king is being directly attacked
    
    kinglocation = get_king_location(team)
    kingcol = kinglocation[0]
    kingrow = kinglocation[1]
    if kinglocation in pths[otherteam]:
        #there is a check
        #either the king moves, the attacking piece is killed, or a piece is put in the way
        escapemoves = []
        if pieceran == 'king':
            escapemoves = gen_moveset('king',kinglocation,team,locs,'yes','yes')

        attackingpieces = []
        killmoves = []

        for piece in data[otherteam]:
            #data moveset doesn't matter as data[otherteam] = datawithoutpiece[otherteam]
            moveset = gen_moveset(piece[0],piece[1],otherteam,locs,'yes','yes')
            if kinglocation in moveset:
                attackingpieces.append(piece[0])
                killmoves.append(piece[1])
        if len(killmoves) > 1:
            #more than one piece attacking (double check)
            killmoves = []
        
        defendmoves = []
        if len(attackingpieces) == 1:
            #avoiding unneeded code if double check
            attacker = attackingpieces[0]
            attackerloc = killmoves[0]
            acol = attackerloc[0]
            arow = attackerloc[1]
            #basically a line connecting the attacking piece to the king
            if (attacker != 'knight') and (attacker != 'pawn1') and (attacker != 'pawn2') and (attackerloc not in gen_moveset('king',kinglocation,team,locs,'yes')):
                 #knights can't be blocked     #pawns can be directly captured       #you can't put something in between if the pieces are adjecant
                 #hopefully a king will never be attacking a king
                 #first up: horizontal/rook/queen/wyvern
                 if arow == kingrow:
                    if columns.index(kingcol) < columns.index(acol):
                        #either to the left
                        #(and now to rip code from move generation algorithms)
                        moves = [chr(item)+arow for item in range(ord(kingcol)+1,ord(acol))]
                        #if the king isn't the piece being attacked there is a really big problem here
                    else:
                        moves = [chr(item)+arow for item in range(ord(acol)+1,ord(kingcol))]
                 elif acol == kingcol:
                    #next vertical/rook/queen/wyvern
                    if rows.index(kingrow) > rows.index(arow):
                        #above the attacker
                        moves = [acol+str(item+1) for item in range(8) if (item > rows.index(arow)) and (item < rows.index(kingrow))]                        
                    else:
                        #below
                        moves = [acol+str(item+1) for item in range(8) if (item < rows.index(arow)) and (item > rows.index(kingrow))]            
                
                        
                 else:
                    #only bishop/queen/wyvern go here (diagonal)
                    leftdiagonalconstant = ord(acol) + rows.index(arow)
                    leftdiagonal = [chr(leftdiagonalconstant-item)+str(item+1) for item in range(8) if leftdiagonalconstant-item > 96 and leftdiagonalconstant-item < 105]
                    rightdiagonalconstant = ord(acol) - rows.index(arow)
                    rightdiagonal = [chr(rightdiagonalconstant+item)+str(item+1) for item in range(8) if rightdiagonalconstant+item > 96 and rightdiagonalconstant+item < 105]
                    if kingcol < acol and kingrow > arow:
                        #above,left
                        i = leftdiagonal.index(attackerloc)
                        x = leftdiagonal.index(kinglocation)
                        moves = leftdiagonal[i+1:x]+leftdiagonal[x+1:i]
                    elif kingcol > acol and kingrow < arow:
                        #below,right
                        i = leftdiagonal.index(attackerloc)
                        x = leftdiagonal.index(kinglocation)
                        moves = leftdiagonal[i+1:x]+leftdiagonal[x+1:i]
                    elif kingcol > acol and kingrow > arow:
                        #above,right
                        i = rightdiagonal.index(attackerloc)
                        x = rightdiagonal.index(kinglocation)
                        moves = rightdiagonal[i+1:x]+rightdiagonal[x+1:i]
                    elif kingcol < acol and kingrow < arow:
                        #below,left
                        i = rightdiagonal.index(attackerloc)
                        x = rightdiagonal.index(kinglocation)
                        moves = rightdiagonal[i+1:x]+rightdiagonal[x+1:i]
            try:
                defendmoves = moves
            except:
                pass
        if pieceran == 'notking':
            checkedmoves = killmoves + defendmoves
        
        if pieceran != 'notking':
            #obviously the piece is the king
            checkedmoves = escapemoves
            for item in checkedmoves:
                #any location that is in checkpaths but not in paths is on the other side of the king as the attacking piece
                if (item not in pths[otherteam]) and (item in checkpths[otherteam]):
                    #the only reason that dictionary was created
                    checkedmoves.remove(item)
            for item in checkedmoves:
                #can't walk into check
                if item in paths[otherteam]:
                    checkedmoves.remove(item)
    else:
        #there is no check
        checkedmoves = False
    return checkedmoves




def is_checkmate(team):
    #the is_check function:
        #there is a check:
            #you can move here to get out (list of moves; CHECK)
            #oh no you can't move at all (empty list; CHECKMATE)
        #there is no check:
            #return False
    try: 
        l = is_check(team) + is_check(team,locations,paths,checkpaths,'king')

        #no way to defend or kill out of the check
        for i in range(5):
            for item in l:
                if item not in paths[team]:
                    l.remove(item)
        
        if l == []:
            return True
        else:
            return False
    except:
        #can't add booleans
        return False




def is_stalemate(team):
    #stalemate: king has no moves, but is not in check
    #aka        king's moveset ==[], is_check == False

    if paths[team] == [] and is_check(team) == False:
        return True
    else:
        return False
    
########## MOVESET GENERATION ##########    
def gen_moveset(piece,location,team,locs=locations,incheckfunction='no',infoolscheck='no',stale='no',kingclause='no'):
    if piece == 'king':
        moveset = gen_king(location,team,locs,stale,kingclause)
    elif piece == 'queen':
        moveset = gen_queen(location,team,locs)
    elif piece == 'bishop':
        moveset = gen_bishop(location,team,locs)
    elif piece == 'knight':
        moveset = gen_knight(location,team,locs)
    elif piece == 'rook':
        moveset = gen_rook(location,team,locs)
    elif piece == 'wyvern':
        moveset = gen_wyvern(location,team,locs)
    else:
        moveset = gen_pawn(location,team,locs)

    if incheckfunction == 'no' and piece != 'king':
        #avoiding an infinite loop in the check function
        isthereacheck = is_check(team,locations,paths,checkpaths,'notking')
    elif incheckfunction =='no' and piece == 'king':
        isthereacheck = is_check(team,locations,paths,checkpaths,'king')
    else:
        isthereacheck = False
        
    if isthereacheck != False:
        #there is a check active, the piece must move to save the king
        if piece == 'notking':
            for item in moveset:
                if item not in isthereacheck:
                    moveset.remove(item)
        #...or the king can just move
        if piece == 'king':
            
            check = is_check(team,locations,paths,checkpaths,'king')
            moveset = check
            #the king cannot capture the attacking piece and fall into another check:
            #the easiest way to do this is to pretend the attacking piece is on the same team as the king
            #if that piece can be 'attacked' by the other team, then it is in their path and therefore unsafe to move to
            if team == 'B':
                otherteam = 'W'
            else:
                otherteam = 'B'
                
            for item in moveset:
                tempdata = {'B': [],
                            'W': []}
                tempdata[team] = data[team]
                otherteamdata = data[otherteam]
                if ['rook',item] in otherteamdata:
                    attacker = 'rook'
                elif ['knight',item] in otherteamdata:
                    attacker = 'knight'
                elif ['bishop',item] in otherteamdata:
                    attacker = 'bishop'
                elif ['queen',item] in otherteamdata:
                    attacker = 'queen'
                elif ['wyvern',item] in otherteamdata:
                    attacker = 'wyvern'
                #not sure if these thre are needed, but better safe than sorry
                elif ['pawn1',item] in otherteamdata:
                    attacker = 'pawn1'
                elif ['pawn2',item] in otherteamdata:
                    attacker = 'pawn2'
                elif ['king',item] in otherteamdata:
                    attacker = 'king'
                ##############################
                else:
                    attacker = None
                if attacker != None:
                    #someone has to be attacking for all this to work...
                    otherteamdata.remove([attacker,item])
                    tempdata[otherteam]= otherteamdata
                    tempdata[team].append([attacker,item])

                    templocations = {'B':[],
                                     'W':[]}

                    for team in tempdata:
                        for piece in tempdata[team]:
                            templocations[team].append(piece[1])

                    temppaths = {'B': [],
                                 'W': []}
                    for team in tempdata:
                        allpaths = []
                        for piece in tempdata[team]:
                            allpaths+=gen_moveset(piece[0],piece[1],team,templocations,'yes')
                            #false check declared to prevent crash
                        returnedpaths = remove_multiples(allpaths)
                        returnedpaths.sort()
                        temppaths[team] = returnedpaths
                    if item in temppaths[otherteam]:
                        #the attacking piece is in the line of sight of another enemy piece
                        moveset.remove(item)
                    
    if piece != 'king' and infoolscheck == 'no':
        #situation: black king at b1, white rook at f1, black knight in between them at c1
        #if it is black's turn, black cannot move the king because it would put its king into check
        #based on how the code is structured, this means that white could actually capture the king

        #to prevent this from happening, we need to go one move ahead and see if there is a check
        #instead of faking a move by the piece in the middle (the knight in the example), it just doesn't exist
        
        datawithoutpiece = {}
        if team == 'B':
            otherteam = 'W'
        else:
            otherteam = 'B'

        datawithoutpiece[otherteam] = data[otherteam]
        teamdata = copy.deepcopy(data[team])
        for item in teamdata:
            if item == [piece,location]:
                teamdata.remove(item)
        datawithoutpiece[team] = teamdata

        locationswithoutpiece = {'B': [],
                                 'W': []}
        for t in datawithoutpiece:
            for p in datawithoutpiece[t]:
                if p[0] != piece:
                    locationswithoutpiece[t].append(p[1])

        pathswithoutpiece ={'B': [],
                            'W': []}
        for t in datawithoutpiece:
            allpaths = []
            for p in datawithoutpiece[t]:
                allpaths+=gen_moveset(p[0],p[1],t,locationswithoutpiece,'yes','yes')
                #false check declared to prevent crash, same with foresighted fool's check
            returnedpaths = remove_multiples(allpaths)
            returnedpaths.sort()
            pathswithoutpiece[t] = returnedpaths

        locationswithoutkingorpiece = {'B':[],
                                       'W':[]}
        checkpathswithoutpiece = {'B':[],
                                  'W':[]}
        for t in datawithoutpiece:
            for p in datawithoutpiece[team]:
                if p[0] != 'king':
                    locationswithoutkingorpiece[team].append(p[1])
        for t in datawithoutpiece:
            allcheckpathswithoutpiece = []
            for p in datawithoutpiece[t]:
                if p[0] != 'king':
                    allcheckpathswithoutpiece+=gen_moveset(p[0],p[1],t,locationswithoutking,'yes','yes')
                    #it's still a false check declaration
            returnedcheckpathswithoutpiece = remove_multiples(allcheckpathswithoutpiece)
            returnedcheckpathswithoutpiece.sort()
            checkpathswithoutpiece[t] = returnedcheckpathswithoutpiece
        
        check = is_check(team,locationswithoutpiece,pathswithoutpiece,checkpathswithoutpiece)
        if check != False:
            #there is a theoretical check without the questioned piece in its current location
            #the moves returned in this case are the "in-between" and "kill" moves
            #these need to be intersected with the regular moveset for the piece
            for i in range(5):
                #once again the mysterious half-remove syndrome
                for item in moveset:
                    if item not in check:
                        moveset.remove(item)

    if piece == 'king':
        #castling:
        #1) the king and rook have not moved yet
        #2) the king is not in check
        #3) no pieces are in between the king and rook
        #4) none of the spaces in between them are "in check"

        if team == 'W':

            #white team castling
            #long castle (left)
            if ['king','yes'] in castles['W'] and ['left','yes'] in castles['W']:
                #1
                if ('b1' not in paths['B']) and ('c1' not in paths['B']) and ('d1' not in paths['B']) and ('e1' not in paths['B']):
                    #2,4
                    alllocs = locations['B'] + locations['W']
                    if ('b1' not in alllocs) and ('c1' not in alllocs) and ('d1' not in alllocs):
                        #3
                        moveset.append('c1')

            #short castle (right)
            if ['king','yes'] in castles['W'] and ['right','yes'] in castles['W']:
                #1
                if ('e1' not in paths['B']) and ('f1' not in paths['B']) and ('g1' not in paths['B']):
                    #2,4
                    alllocs = locations['B'] + locations['W']
                    if ('f1' not in alllocs) and ('g1' not in alllocs):
                        #3
                        moveset.append('g1')

        elif team == 'B':

            #black team castling
            #long castle (left)
            if ['king','yes'] in castles['B'] and ['left','yes'] in castles['B']:
                #1
                if ('b8' not in paths['W']) and ('c8' not in paths['W']) and ('d8' not in paths['W']) and ('e8' not in paths['B']):
                    #2,4
                    alllocs = locations['B'] + locations['W']
                    if ('b8' not in alllocs) and ('c8' not in alllocs) and ('d8' not in alllocs):
                        #3
                        moveset.append('c8')

            #short castle (right)
            if ['king','yes'] in castles['B'] and ['right','yes'] in castles['B']:
                #1
                if ('e8' not in paths['W']) and ('f8' not in paths['W']) and ('g8' not in paths['W']):
                    #2,4
                    alllocs = locations['B'] + locations['W']
                    if ('f8' not in alllocs) and ('g8' not in alllocs):
                        #3
                        moveset.append('g8')
    return moveset

def gen_king(location,team,locs=locations,stale='no',kingclause='no'):
    if team == 'B':
        otherteam = 'W'
    else:
        otherteam = 'B'

    row = location[1]
    numrow = rows.index(row)
    
    column = location[0]
    numcolumn = columns.index(column)
    
    leftcol = numcolumn-1
    rightcol = numcolumn+1
    aboverow = numrow-1
    belowrow = numrow+1

    if leftcol >= 0:
        left = columns[leftcol]
    else:
        left = ''

    if rightcol < 8:
        right = columns[rightcol]
    else:
        right = ''

    if aboverow >= 0:
        above = rows[aboverow]
    else:
        above = ''

    if belowrow < 8:
        below = rows[belowrow]
    else:
        below = ''
        
    moveset = [left+above,
               left+row,
               left+below,
               column+above,
               column+below,
               right+above,
               right+row,
               right+below]

    for item in range(5):
        #each loop takes out half the invalid moves for some reason, so at most 5 loops are needed
        for item in moveset:
            #avoiding collision of pieces on the same team
            if item in locs[team]:
                moveset.remove(item)
            #removing nonexistent moves
            elif len(item) != 2:
                moveset.remove(item)
            #king cannot walk into a check
            elif stale != 'yes' and kingclause == 'no':
                if item in paths[otherteam]:
                    moveset.remove(item)

    if kingclause == 'no':
        locationswithoutteamking = copy.deepcopy(locations)
        locationswithoutteamking[team].remove(get_king_location(team))
        pathswithoutteamking = {'B':[],
                                'W':[]}
        for team in data:
            allpathswithoutteamking = []
            for piece in data[team]:
                allpathswithoutteamking+=gen_moveset(piece[0],piece[1],team,locationswithoutteamking,'yes','yes','no','yes')
                #false check declared to prevent crash
            returnedpathswithoutteamking = remove_multiples(allpathswithoutteamking)
            returnedpathswithoutteamking.sort()
            pathswithoutteamking[team] = returnedpathswithoutteamking
            
        for i in range(5):
            for item in moveset:
                if item in pathswithoutteamking[otherteam]:
                    moveset.remove(item)

    return moveset

def gen_rook(location,team,locs=locations):
    if team == 'B':
        otherteam = 'W'
    else:
        otherteam = 'B'
        
    row = location[1]
    numrow = rows.index(row)
    
    column = location[0]
    numcolumn = columns.index(column)
    unicodecolumn = ord(column)
    
    movesincolumnbelow = [column+str(item+1) for item in range(8) if item < numrow]
    movesincolumnbelow.reverse()
    #ordering the moves by distance from the rook
    movesincolumnabove = [column+str(item+1) for item in range(8) if item > numrow]
    movesinrowleft = [chr(item)+row for item in range(97,unicodecolumn)]
    movesinrowleft.reverse()
    #ordering the moves by distance from the rook
    movesinrowright = [chr(item)+row for item in range(unicodecolumn+1,105)]
    #lists of all the possible unobstructed moves to the left, to the right, above, and below ordered by distance
 
    othersincolumn = [item for item in locs[team] if item[0] == column] + [item for item in locs[otherteam] if item[0] == column]
    othersinrow = [item for item in locs[team] if item[1] == row] + [item for item in locs[otherteam] if item[1] == row]
    #the locations of every piece in the game in the same column/row as the rook
    
    othersincolumnabove = [item for item in othersincolumn if rows.index(item[1]) > numrow]
    #the location of every piece in the game that is above the rook in the same column
    othersincolumnabove.sort()
    #putting the pieces in order by distance (i.e. d6 d7 d8)
    if othersincolumnabove != []:
        #the closest piece
        closestpieceabove = othersincolumnabove[0]
    else:
        #if there are no pieces above
        closestpieceabove = 0
    
    othersincolumnbelow = [item for item in othersincolumn if rows.index(item[1]) < numrow]
    #the location of every piece in the game that is below the rook in the same column
    othersincolumnbelow.sort()
    #putting the pieces in reverse order by distance (i.e. d1 d2 d3 d4)
    othersincolumnbelow.reverse()
    #putting the pieces in order by distance (i.e. d4 d3 d2 d1)
    if othersincolumnbelow != []:
        #the closest piece
        closestpiecebelow = othersincolumnbelow[0]
    else:
        #if there are no pieces below
        closestpiecebelow = 0
        
    othersinrowleft = [item for item in othersinrow if columns.index(item[0]) < numcolumn]
    #the location every other piece in the game that is to the left of the rook in the same row
    othersinrowleft.sort()
    #putting the pieces in reverse order by distance (i.e. a5 b5 c5)
    othersinrowleft.reverse()
    #putting the pieces in order by distance (c5 b5 a5)
    if othersinrowleft != []:
        #the closest piece
        closestpieceleft = othersinrowleft[0]
    else:
        #if there are no pieces to the left
        closestpieceleft = 0
    
    othersinrowright = [item for item in othersinrow if columns.index(item[0]) > numcolumn]
    #the location every other piece in the game that is to the right of the rook in the same row
    othersinrowright.sort()
    #putting the pieces in order by distance (i.e. e5 f5 g5 h5)
    if othersinrowright != []:
        #the closest piece 
        closestpieceright = othersinrowright[0]
    else:
        #if there are no pieces to the right
        closestpieceright = 0

    if closestpieceabove != 0:
        distance = movesincolumnabove.index(closestpieceabove)
        #how many spaces away the closest piece going up is
        if closestpieceabove in locs[team]:
            #can only move as far as space before closest ally
            movesabove = movesincolumnabove[:distance]
        else:
            #can only move as far as space of closest enemy piece
            movesabove = movesincolumnabove[:distance]
            movesabove.append(closestpieceabove)
    else:
        movesabove = movesincolumnabove
        #no obstructions
            
    if closestpiecebelow != 0:
        distance = movesincolumnbelow.index(closestpiecebelow)
        #how many spaces away the closest piece going down is
        if closestpiecebelow in locs[team]:
            #can only move as far as space before closest ally
            movesbelow = movesincolumnbelow[:distance]
        else:
            #can only move as far as space of closest enemy piece
            movesbelow = movesincolumnbelow[:distance]
            movesbelow.append(closestpiecebelow)
    else:
        movesbelow = movesincolumnbelow
        #no obstructions
        
    if closestpieceleft != 0:
        distance = movesinrowleft.index(closestpieceleft)
        #how many spaces away the closest piece to the left is
        if closestpieceleft in locs[team]:
            #can only move as far as space before closest ally
            movesleft = movesinrowleft[:distance]
        else:
            #can only move as far as space of closest enemy piece
            movesleft = movesinrowleft[:distance]
            movesleft.append(closestpieceleft)
        
    else:
        movesleft = movesinrowleft
        #no obstructions
        
    if closestpieceright != 0:
        distance = movesinrowright.index(closestpieceright)
        #how many spaces away the closest piece to the right is
        if closestpieceright in locs[team]:
            #can only move as far as space before closest ally
            movesright = movesinrowright[:distance]
        else:
            #can only move as far as space of closest enemy piece
            movesright = movesinrowright[:distance]
            movesright.append(closestpieceright)
    else:
        movesright = movesinrowright
        #no obstructions
        
    #and now the moment you've all been waiting for
    moveset = movesabove + movesbelow + movesleft + movesright
    return moveset

def gen_bishop(location,team,locs=locations):
    if team == 'B':
        otherteam = 'W'
    else:
        otherteam = 'B'

    row = location[1]
    numrow = rows.index(row)

    column = location[0]
    unicodecolumn = ord(column)
    
    leftdiagonalconstant = unicodecolumn - numrow

    #every diagonal with a negative slope follows the equation ord(column) - numrow = k 
    leftdiagonal = [chr(leftdiagonalconstant+item)+str(item+1) for item in range(8) if leftdiagonalconstant+item > 96 and leftdiagonalconstant+item < 105]

    i = leftdiagonal.index(location)
    upleftdiagonal = leftdiagonal[:i]
    upleftdiagonal.reverse()
    #furthest -> closest becomes closest -> furthest 
    downrightdiagonal = leftdiagonal[i+1:]

    rightdiagonalconstant = unicodecolumn + numrow
    #every diagonal with a positive slope is in the form ord(column) + numrow = k
    rightdiagonal = [chr(rightdiagonalconstant-item)+str(item+1) for item in range(8) if rightdiagonalconstant-item > 96 and rightdiagonalconstant-item < 105]
    
    i = rightdiagonal.index(location)
    downleftdiagonal = rightdiagonal[:i]
    downleftdiagonal.reverse()
    #furthest -> closest becomes closest -> furthest 
    uprightdiagonal = rightdiagonal[i+1:]

    othersinupleftdiagonal = [item for item in locs[team] if item in upleftdiagonal]+ \
                             [item for item in locs[otherteam] if item in upleftdiagonal]
    #the locations of every piece in the game that is in the upper left diagonal of the bishop
    othersinupleftdiagonal.sort()
    #reverse order of distance from the bishop (i.e. a2 b3 c4)
    othersinupleftdiagonal.reverse()
    #in order of distance (c4 b3 a2)
    
    othersinuprightdiagonal = [item for item in locs[team] if item in uprightdiagonal]+ \
                              [item for item in locs[otherteam] if item in uprightdiagonal]
    #the locations of every piece in the game that is in the upper right diagonal of the bishop
    othersinuprightdiagonal.sort()
    #reverse order of distance from the bishop (i.e. a8 b7 c6)
    othersinuprightdiagonal.reverse()
    #in order of distance (c6 b7 a8)
    
    othersindownleftdiagonal = [item for item in locs[team] if item in downleftdiagonal]+ \
                               [item for item in locs[otherteam] if item in downleftdiagonal]
    #the locations of every piece in the game that is in the lower left diagonal of the bishop
    othersindownleftdiagonal.sort()
    #in order of distance (i.e. e4 f3 g2 h1)
    
    othersindownrightdiagonal = [item for item in locs[team] if item in downrightdiagonal]+ \
                                [item for item in locs[otherteam] if item in downrightdiagonal]
    #the locations of every piece in the game that is in the lower right diagonal of the bishop
    othersindownrightdiagonal.sort()
    #in order of distance (i.e. e6 f7 g8)

    if othersinupleftdiagonal != []:
        closestpieceupleft = othersinupleftdiagonal[0]
        #closest
    else:
        closestpieceupleft = 0
        #no pieces
    
    if othersinuprightdiagonal != []:
        closestpieceupright = othersinuprightdiagonal[0]
        #closest
    else:
        closestpieceupright = 0
        #no pieces

    if othersindownleftdiagonal != []:
        closestpiecedownleft = othersindownleftdiagonal[0]
        #closest
    else:
        closestpiecedownleft = 0
        #no pieces
    
    if othersindownrightdiagonal != []:
        closestpiecedownright = othersindownrightdiagonal[0]
        #closest
    else:
        closestpiecedownright = 0
        #no pieces

    if closestpieceupleft != 0:
        distance = upleftdiagonal.index(closestpieceupleft)
        #how many spaces away the closest piece up and to the left is
        if closestpieceupleft in locs[team]:
            #can only move as far as space before closest ally
            upleft = upleftdiagonal[:distance]
        else:
            #can only move as far as space of closest enemy piece
            upleft = upleftdiagonal[:distance]
            upleft.append(closestpieceupleft)
    else:
        upleft = upleftdiagonal
        #no obstructions
        
    if closestpieceupright != 0:
        distance = uprightdiagonal.index(closestpieceupright)
        #how many spaces away the closest piece up and to the right is
        if closestpieceupright in locs[team]:
            #can only move as far as space before closest ally
            upright = uprightdiagonal[:distance]
        else:
            #can only move as far as space of closest enemy piece
            upright = uprightdiagonal[:distance]
            upright.append(closestpieceupright)
    else:
        upright = uprightdiagonal
        #no obstructions

    if closestpiecedownleft != 0:
        distance = downleftdiagonal.index(closestpiecedownleft)
        #how many spaces away the closest piece down and to the left is
        if closestpiecedownleft in locs[team]:
            #can only move as far as space before closest ally
            downleft = downleftdiagonal[:distance]
        else:
            #can only move as far as space of closest enemy piece
            downleft = downleftdiagonal[:distance]
            downleft.append(closestpiecedownleft)
    else:
        downleft = downleftdiagonal
        #no obstructions
        
    if closestpiecedownright != 0:
        distance = downrightdiagonal.index(closestpiecedownright)
        #how many spaces away the closest piece down and to the right is
        if closestpiecedownright in locs[team]:
            #can only move as far as space before closest ally
            downright = downrightdiagonal[:distance]
        else:
            #can only move as far as space of closest enemy piece
            downright = downrightdiagonal[:distance]
            downright.append(closestpiecedownright)
    else:
        downright = downrightdiagonal
        #no obstructions

    moveset = upleft + upright + downleft + downright
    return moveset

def gen_queen(location,team,locs=locations):
    diagonals = gen_bishop(location,team,locs)
    horizontals = gen_rook(location,team,locs)
    moveset = horizontals + diagonals
    return moveset

def gen_knight(location,team,locs=locations):
    row = location[1]
    numrow = rows.index(row)
    
    column = location[0]
    numcolumn = columns.index(column)

    if numrow > 0:
        rowabove1 = rows[numrow-1]
    else:
        rowabove1 = ''
    if numrow > 1:
        rowabove2 = rows[numrow-2]
    else:
        rowabove2 = ''
        
    if numrow < 7:
        rowbelow1 = rows[numrow+1]
    else:
        rowbelow1 = ''
    if numrow < 6:
        rowbelow2 = rows[numrow+2]
    else:
        rowbelow2 = ''
        
    if numcolumn > 0:
        leftcolumn1 = columns[numcolumn-1]
    else:
        leftcolumn1 = ''
    if numcolumn > 1:
        leftcolumn2 = columns[numcolumn-2]
    else:
        leftcolumn2 = ''

    if numcolumn < 7:
        rightcolumn1 = columns[numcolumn+1]
    else:
        rightcolumn1 = ''
    if numcolumn < 6:
        rightcolumn2 = columns[numcolumn+2]
    else:
        rightcolumn2 = ''

    moveset = [leftcolumn1+rowabove2,
               rightcolumn1+rowabove2,
               leftcolumn2+rowabove1,
               rightcolumn2+rowabove1,
               leftcolumn2+rowbelow1,
               rightcolumn2+rowbelow1,
               leftcolumn1+rowbelow2,
               rightcolumn1+rowbelow2]
    for item in moveset:
        #avoiding collision of pieces on the same team
        if item in locs[team]:
            moveset.remove(item)
    for item in range(5):
        #each loop takes out half the invalid moves for some reason, so at most 5 loops are needed
        for item in moveset:
            if len(item) != 2:
                moveset.remove(item)
    return moveset

def gen_pawn(location,team,locs=locations):
    if team == 'B':
        otherteam = 'W'
    else:
        otherteam = 'B'

    row = location[1]
    numrow = rows.index(row)
    
    column = location[0]
    numcolumn = columns.index(column)

    moveset = []

    #moves going forward
    alllocations = locs[team] + locs[otherteam]
    if team == 'W':
        if numrow < 7:
            if row == '2':
                if column+'3' not in alllocations:
                    moveset.append(column+'3')
                    if column+'4' not in alllocations:
                        #cannot move the initial 2 spaces if there is a piece on the first
                        moveset.append(column+'4')
            else:
                if column+rows[numrow+1] not in alllocations:
                    moveset.append(column+rows[numrow+1])
    else:
        #black team
        if numrow > 0:
            if row == '7':
                if column+'6' not in alllocations:
                    moveset.append(column+'6')
                    if column+'5' not in alllocations:
                        #cannot move the initial 2 spaces if there is a piece on the first
                        moveset.append(column+'5')
            else:
                if column+rows[numrow-1] not in alllocations:
                    moveset.append(column+rows[numrow-1])

    #traditional capturing moves            
    possiblecaptures = []
    
    if team =='W' and numrow < 7:
        if numcolumn > 0:
            possiblecaptures.append(columns[numcolumn-1]+rows[numrow+1])
            leftspace = columns[numcolumn-1]+row
        if numcolumn < 7:
            possiblecaptures.append(columns[numcolumn+1]+rows[numrow+1])
            rightspace = columns[numcolumn+1]+row
        #en passant
        if row == '5':
            if numcolumn > 0:
                if ['pawn2',leftspace] in data[otherteam]:
                    moveset.append(columns[numcolumn-1]+'6')
            if numcolumn < 7:
                if ['pawn2',rightspace] in data[otherteam]:
                    moveset.append(columns[numcolumn+1]+'6')
        
    elif team =='B' and numrow > 0:
        if numcolumn > 0:
            possiblecaptures.append(columns[numcolumn-1]+rows[numrow-1])
            leftspace = columns[numcolumn-1]+row
        if numcolumn < 7:
            possiblecaptures.append(columns[numcolumn+1]+rows[numrow-1])
            rightspace = columns[numcolumn+1]+row
        #en passant
        if row == '4':
            if numcolumn > 0:
                if ['pawn2',leftspace] in data[otherteam]:
                    moveset.append(columns[numcolumn-1]+'3')
            if numcolumn < 7:
                if ['pawn2',rightspace] in data[otherteam]:
                    moveset.append(columns[numcolumn+1]+'3')

    for item in possiblecaptures:
        if item in locs[otherteam]:
            moveset.append(item)

    return moveset

def gen_wyvern(location,team,locs=locations):
    getready = gen_knight(location,team,locs)
    todie = gen_queen(location,team,locs)
    existenceisfutile = getready + todie
    return existenceisfutile


########## NOW FOR THE HTML ##########






########## DROP DOWN MENU FUNCTIONS ##########
def menu1(team):
    dropdownpieces = ''
    listofpieces = []
    for piece in data[team]:
        if piece[0] == 'pawn1' or piece[0] == 'pawn2':
            listofpieces.append('pawn')
        else:
            listofpieces.append(piece[0])
    l = remove_multiples(listofpieces)
    l.sort()
    for piece in l:
        dropdownpieces+=('\n<input type="radio" name="piece" value="%(piece)s">%(piece)s</option>'%{'piece':piece})
    return dropdownpieces

def menu2(team):
    dropdownmovefrom = ''
    l = []
    for piece in data[team]:
        l.append(piece[1])
    l.sort()
    for piece in l:
        dropdownmovefrom+=('\n<input type="radio" name="location" value="%(location)s">%(location)s</option>'%{'location':piece})
    return dropdownmovefrom

def menu3(team):
    dropdownmoveto = ''
    for num in range(97,105):
        col = chr(num)
        dropdownmoveto+=('\n<select name="move%s">'%col)
        dropdownmoveto+=('\n<option value="--">--</option>')
        for row in range(1,9):
            d = {'col': col,
                 'space': col+str(9-row)}
            dropdownmoveto+=('\n<option value="%(space)s">%(space)s</option>'%d)
        dropdownmoveto+=('\n<select>\n')
    return dropdownmoveto

########## DATA WRITING FUNCTIONS ##########
def writedata():
    for team in data:
        datafile = open(team+'data.txt','w')
        for piece in data[team]:
            datafile.write((',').join(piece)+'\n')
        datafile.close()

def writecastles():
    for team in castles:
        datafile = open(team+'castles.txt','w')
        for item in castles[team]:
            datafile.write((',').join(item)+'\n')
        datafile.close()

########## TEMPLATES ##########
menu_template = '''
<form>
Pieces: %(piecemenu)s <br>
Move From: %(locationmenu)s <br>
Move To: %(movetomenu)s <br>
<input type="submit" name="button" value="submit"></input>
</form>
<font color="red">%(error)s</font>
'''

board = '''
<style type="text/css">
table {
background-image: url(/html/board.png);
background-size: 100%% 100%%;
}
</style>
<table border="0" cellpadding="0">
%(8)s
%(7)s
%(6)s
%(5)s
%(4)s
%(3)s
%(2)s
%(1)s
</table>
'''
########## GET DATA ##########
piece = urldata.getvalue('piece')
location = urldata.getvalue('location')
movea = urldata.getvalue('movea')
moveb = urldata.getvalue('moveb')
movec = urldata.getvalue('movec')
moved = urldata.getvalue('moved')
movee = urldata.getvalue('movee')
movef = urldata.getvalue('movef')
moveg = urldata.getvalue('moveg')
moveh = urldata.getvalue('moveh')
button = urldata.getvalue('button')

########## MOVE LIST ##########
inputmoves = [movea,moveb,movec,moved,movee,movef,moveg,moveh]
for i in range(4):
    for item in inputmoves:
        if item == '--' or item == None:
            inputmoves.remove(item)

########## ERROR ##########
error = ''
#default

def errors(team):
    cont = False
    if len(inputmoves) > 1:
        #the user chose more than one move
        error = 'Too many moves chosen'
    elif len(inputmoves) == 0:
        #no moves chosen
        error = 'No moves chosen'
    else:
        #only 1 selected move
        move = inputmoves[0]

        global piece
        if piece == 'pawn':
            try:
                data[team].index(['pawn1',location])
                #'cont(inue)' means that the code will continue going through tests, as I can't put them inside a try block
                cont = True
                global piece
                piece = 'pawn1'
            except:
                try:
                    data[team].index(['pawn2',location])
                    cont = True
                    global piece
                    piece = 'pawn2'
                except:
                    error = 'That piece is not on that space'
        else:
            try:
                #verifying if the piece called is on the space called
                data[team].index([piece,location])
                cont = True
            except:
                error = 'That piece is not on that space'

    if cont == True:
        #continuing on with tests:
        if move in gen_moveset(piece,location,team):
            error = ''
        else:
            error = "Invalid move"
    return error
    
########## TURN MECHANISM ##########
def changeturn(team='W'):
    turnfile = open('turn.txt','w')
    if team == 'W':
        turnfile.write('W')
    else:
        turnfile.write('B')
    turnfile.close()
########## BUTTON ##########
if button != None:
    #not a new game
    teamturn = open('turn.txt').read()
    
    #loading data
    dataformat('B')
    dataformat('W')
    castleformat('B')
    castleformat('W')

    compile_splitdata()
    compile_locations()
    compile_pieces()
    compile_paths()
    compile_locationswithoutking()
    compile_checkpaths()
    
    error = errors(teamturn)
    if error == '':
        if teamturn == 'B':
            otherteamturn = 'W'
        else:
            otherteamturn = 'B'
                    
        #move being made
        data[teamturn].remove([piece,location])
        data[teamturn].append([piece,inputmoves[0]])

        #castling
        #white
        if teamturn == 'W' and piece == 'king' and location == 'e1':
            if inputmoves[0] == 'c1':
                #long castle
                data[teamturn].remove(['rook','a1'])
                data[teamturn].append(['rook','d1'])
            elif inputmoves[0] == 'g1':
                #short castle
                data[teamturn].remove(['rook','h1'])
                data[teamturn].append(['rook','f1'])
        #black
        if teamturn == 'B' and piece == 'king' and location == 'e8':
            if inputmoves[0] == 'c8':
                #long castle
                data[teamturn].remove(['rook','a8'])
                data[teamturn].append(['rook','d8'])
            elif inputmoves[0] == 'g8':
                #short castle
                data[teamturn].remove(['rook','h8'])
                data[teamturn].append(['rook','f8'])

        #possible nullification of castling:
        if teamturn == 'W':
            if piece == 'rook':
                if location == 'a1':
                    if ['left','yes'] in castles['W']:
                        castles['W'].remove(['left','yes'])
                        castles['W'].append(['left','no'])
                if location == 'h1':
                    if ['right','yes'] in castles['W']:
                        castles['W'].remove(['right','yes'])
                        castles['W'].append(['right','no'])
            if piece == 'king':
                if location == 'e1':
                    if ['king','yes'] in castles['W']:
                        castles['W'].remove(['king','yes'])
                        castles['W'].append(['king','no'])
        elif teamturn == 'B':
            if piece == 'rook':
                if location == 'a8':
                    if ['left','yes'] in castles['B']:
                        castles['B'].remove(['left','yes'])
                        castles['B'].append(['left','no'])
                if location == 'h8':
                    if ['right','yes'] in castles['B']:
                        castles['B'].remove(['right','yes'])
                        castles['B'].append(['right','no'])
            if piece == 'king':
                if location == 'e8':
                    if ['king','yes'] in castles['B']:
                        castles['B'].remove(['king','yes'])
                        castles['B'].append(['king','no'])
            
        #all special pawns revert
        for p in data[teamturn]:
            if p[0] == 'pawn2':
                loc = p[1]
                data[teamturn].remove(['pawn2',loc])
                data[teamturn].append(['pawn1',loc])
                
        #possible capturing
        if inputmoves[0] in splitdata[otherteamturn]:
            cappedpiece = splitdata[otherteamturn][inputmoves[0]]
            data[otherteamturn].remove([cappedpiece,inputmoves[0]])

        #en passant
        #white moving up
        if piece == 'pawn1' and (location in [chr(i)+'5' for i in range(97,105)]) and (inputmoves[0])[1] != location[1]:
            #white team pawn moving from row 5 whose move is not in the same column (capturing) MIGHT be en passant
            move = inputmoves[0]
            movecol = move[0]
            moverow = move[1]
            cappedpiece = movecol+rows[rows.index(moverow)-1]
            try:
                data[otherteamturn].remove(['pawn2',cappedpiece])
            except:
                pass

        #black moving down
        if piece == 'pawn1' and (location in [chr(i)+'4' for i in range(97,105)]) and (inputmoves[0])[1] != location[1]:
            move = inputmoves[0]
            movecol = move[0]
            moverow = move[1]
            cappedpiece = movecol+rows[rows.index(moverow)+1]
            try:
                data[otherteamturn].remove(['pawn2',cappedpiece])
            except:
                pass
                #setting up en passant
            
        if piece == 'pawn1' and (location in ([chr(i)+'7' for i in range(97,105)]+[chr(i)+'2' for i in range(97,105)])) \
                                 and (inputmoves[0] in ([chr(i)+'5' for i in range(97,105)]+[chr(i)+'4' for i in range(97,105)])):
            data[teamturn].remove(['pawn1',inputmoves[0]])
            data[teamturn].append(['pawn2',inputmoves[0]])
            
        #pawn promotion
        for item in data[teamturn]:
            if item[0] == 'pawn1' and item[1] in ([chr(i)+'8' for i in range(97,105)]+[chr(i)+'1' for i in range(97,105)]):
                data[teamturn].append(['wyvern',item[1]])
                data[teamturn].remove(item)


        
        #writing data
        writedata()
        writecastles()
        
        dataformat('B')
        dataformat('W')
        castleformat('B')
        castleformat('W')
        compile_splitdata()
        compile_locations()
        compile_pieces()
        compile_paths()
        compile_locationswithoutking()
        compile_checkpaths()
        
        if is_checkmate(otherteamturn) == True:
            check = 'Checkmate! %s wins!'%teamturn
        elif is_check(otherteamturn) != False:
            check = 'Check! (%s is under attack)'%otherteamturn
        elif is_stalemate(otherteamturn) == True:
            check = 'Stalemate!'
        else:
                check = ''
        
        changeturn(otherteamturn)
        teamturn = open('turn.txt').read()


    
else:
    #new game
    dataformat('B',True)
    dataformat('W',True)
    castleformat('B',True)
    castleformat('W',True)
    changeturn()
    teamturn = 'W'
    check = ''
    
    #saving config
    writedata()
    writecastles()

    compile_splitdata()
    compile_locations()
    compile_pieces()
    compile_paths()
    compile_locationswithoutking()
    compile_checkpaths()

########## MENU DISPLAY ##########
menu1 = menu1(teamturn)
menu2 = menu2(teamturn)
menu3 = menu3(teamturn)

menus = menu_template%{'piecemenu': menu1,
                       'locationmenu': menu2,
                       'movetomenu': menu3,
                       'error': error}

########## CHESSBOARD ##########
alllocations = locations['B']+locations['W']
boarddata = {'1':{},
             '2':{},
             '3':{},
             '4':{},
             '5':{},
             '6':{},
             '7':{},
             '8':{}}

for team in data:
    if team == 'B':
        fileprefix = 'black'
    else:
        fileprefix = 'white'
    for piece in data[team]:
        loc = piece[1]
        col = loc[0]
        row = loc[1]
        if piece[0] == 'pawn1' or piece[0] == 'pawn2':
            boarddata[row][col] = fileprefix+'pawn.png'
        else:
            boarddata[row][col] = fileprefix+piece[0]+'.png'
    for col in [chr(uni) for uni in range(97,105)]:
        for row in [str(i+1) for i in range(8)]:
            if col+row not in alllocations:
                #no piece on the space
                boarddata[row][col] = 'blank.png'

row8 = boarddata['8']
row7 = boarddata['7']
row6 = boarddata['6']
row5 = boarddata['5']
row4 = boarddata['4']
row3 = boarddata['3']
row2 = boarddata['2']
row1 = boarddata['1']

def gen_row_html(row):
    html = ''
    html += '<tr height="100" width="800">'
    for item in [chr(i) for i in range(97,105)]:
        try:
            html += '<td><img src="/html/%s" onload="this.width/=2;" /></td>'%row[item]
        except:
            #when a piece moves off a space
            html += '<td><img src="%s" onload="this.width/=2;" /></td>'%'blank.png'
    html += '</tr>'
    return html

htmlrow8 = gen_row_html(row8)
htmlrow7 = gen_row_html(row7)
htmlrow6 = gen_row_html(row6)
htmlrow5 = gen_row_html(row5)
htmlrow4 = gen_row_html(row4)
htmlrow3 = gen_row_html(row3)
htmlrow2 = gen_row_html(row2)
htmlrow1 = gen_row_html(row1)

chessboard =  board%{'8':htmlrow8,
                     '7':htmlrow7,
                     '6':htmlrow6,
                     '5':htmlrow5,
                     '4':htmlrow4,
                     '3':htmlrow3,
                     '2':htmlrow2,
                     '1':htmlrow1}


########## DISPLAY ##########
print chessboard
print menus
try:
    print '<hr><font color="red">%s</font>'%check
except:
    pass
