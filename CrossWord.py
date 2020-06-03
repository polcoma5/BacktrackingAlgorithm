# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import time

#################################  GLOBAL VARS #####################################

# Two files lists for iterate over it.

crossword_matrix = ["crossword_CB.txt","crossword_A.txt"]
crossword_dic = ["diccionari_CB.txt","diccionari_A.txt"]

class Crossword:

    ##################################################################################################################################
    ''' class init '''
    def __init__(self,dict_files = [], cross_files = [], row_size = 0, col_size = 0, dictionary={}, empty = None, debug=True):
        
        self.cross_files = cross_files
        self.dict_files = dict_files
        self.col_size = col_size
        self.row_size = row_size
        self.debug = debug

        self.crossword = None           # -> stores crossword matrix in a np.array style from file.
        self.dictionary = dictionary    # -> stores all words in a np array by using it's lenght as an index of dictionary.
        self.empty_spaces_list = empty  # -> each value points to a x,y postion and contain the options to fill the gaps
        self.empty_crossword = None     # -> empty crossword (np array) who will be filled and used to check constraints.

        self.last_word = []

        self.total_word_spaces = 0           # -> how many word empty spaces
        self.total_empty_spaces = 0
        self.index_ptr = 0              # -> indicate empty_spaces_list position to read (pointer) initial = 0  
        self.index_tmp = 0
    
        self.getProgramOptions()





    ##################################################################################################################################
    def getProgramOptions(self):
        op = ''
        while op != '0':
            op = raw_input("Escull el crossword a resoldre: \n1.- crossword_CB\n2.- crossword_A\n\n")
            
            if op == '1':
                self.readCrossword(self.cross_files[0])
                self.readDic(self.dict_files[0])
                break
            elif op == '2':
                self.readCrossword(self.cross_files[1])
                self.readDic(self.dict_files[1])
                break
        

        self.createIndexCross()


    ##################################################################################################################################
    '''
    # -> Creates a crossword mesh from a given filename.
    # -> init sizes (row, col)        
    # -> creates empty crossword that will be filled
    # -> @return; m (size of col) , n (size of rows) and a matrix containing the crossword.
    '''        
    def readCrossword(self,filename):
        
        self.crossword = pd.read_csv(filepath_or_buffer = filename, delimiter = '\t',header = -1, dtype = str).values
        self.row_size = len(self.crossword) 
        self.col_size = len(self.crossword[0]) 
        self.empty_crossword = np.zeros((self.row_size,self.col_size), dtype = object)
           
        if self.debug: 
            print 'Using crossword matrix filename: %s' % filename ,'\n'
            print 'Empty crossword:\n',self.empty_crossword,'\n\nCrossword:\n',self.crossword

    ##################################################################################################################################
    '''
    # -> using asarray instead np.append() it makes a copy before append. 

    # -> Load dictionari from a given filename; stores all words by its lenght.
    # -> @return the dictionari
    '''
    def readDic(self,filename):
        
        tmp = []
        with open(filename, 'r') as dic_file:
            for word in dic_file.readlines():
                w = str(word.rstrip())
                if len(w) <= self.col_size or len(w) <= self.row_size:    
                    if not self.dictionary.has_key(str(len(w))): 
                        arr = np.array([w])
                        #tmp.append(arr)
                        self.dictionary[str(len(w))] = np.asarray(arr)
                    else:
                        arr = self.dictionary[str(len(w))]
                        arr = np.append(arr,[w])
                        self.dictionary[str(len(w))] = np.asarray(arr)

                    del tmp[:]
        

        if self.debug: 
            print 'Using dictiornary filename: %s' % filename ,'\n'
            print 'Dictionary load succesfully! \n'
            print 'Dictionary:'
            for key in self.dictionary.keys():
                print key,' ',self.dictionary[str(key)]
            print '\n'
     
    ##################################################################################################################################
    '''
    # -> Load self.empty_spaces_list as follow: [ [0,0][1,2][-1,7] , [1,0][-1,3], [2,0][1,2] ... ]
    # -> Set self.total_word_spaces
    '''  
    def calcWordLen(self,r,c,direction):

        word_len = 0
        word_lenH = word_lenV = 0
        
        word_len = 0
        word_lenH = word_lenV = 0
        
        if direction == 0:
            czero = c

            for c in range(c,self.col_size):
                if self.crossword[r,c] == '#':
                    break
                else:
                    word_lenH+=1

            self.empty_spaces_list[self.index_tmp] = np.array(np.asarray([[r,czero],[1,word_lenH]]), dtype=object)
            self.index_tmp += 1
            c = czero
            rzero = r
            for r in range(r,self.row_size):
                if self.crossword[r,c] == '#':
                    break
                else:
                    word_lenV+=1
            r = rzero
        
            self.empty_spaces_list[self.index_tmp] = np.array(np.asarray([[rzero,c],[-1,word_lenV]]), dtype=object)
            self.total_word_spaces += 2
            self.index_tmp+=1
        
        elif direction == 1:  

            czero = c
            for c in range(c,self.col_size):
                if self.crossword[r,c] =='#':
                    break
                else:
                    word_len+=1

            self.empty_spaces_list[self.index_tmp] = np.array(np.asarray([[r,czero],[1,word_len]]), dtype=object)
            self.total_word_spaces += 1
            self.index_tmp +=1
            
        
        else:  
            rzero = r
            for r in range(r,self.row_size):
                if self.crossword[r,c]=='#':
                    break
                else:
                    word_len += 1
            
            self.empty_spaces_list[self.index_tmp] = np.array([[rzero,c],[-1,word_len]], dtype=object)
            self.total_word_spaces += 1
            self.index_tmp+=1

        return self.index_tmp
        
    ##################################################################################################################################
    '''
    # -> Returns a np array which can contain 3 items as maximum 1.-[px,py] 2.[dir,wrd_len] 3.-[dir,wrd_len].
    # -> CASES: len(array) > 2 ? right word lenght = array[0][1][1] ; down word lenght = array[0][2][1]
    '''
    def createIndexCross(self):
        
        self.empty_spaces_list = np.empty([(self.row_size * self.col_size)], dtype = object)     
        
        index = 0
        total_empty = 0
        
        for r in range(self.row_size):
            for c in range(self.col_size):
                if (self.crossword[r,c] != '0' and self.crossword[r,c] != '#'): 
                    
                    if ((r==0 and (c==0 or (self.crossword[r][c-1]=='#' and c<self.row_size))) or (c==0 or (self.crossword[r][c-1]=='#' and c<self.row_size))):
                        direction = 1
                        
                    if ((c==0 and (r==0 or (self.crossword[r-1][c]=='#' and r<self.col_size))) or (r==0 or(self.crossword[r-1][c]=='#' and r<self.col_size))):
                        if direction == 1:
                            direction = 0
                            
                        else: 
                            direction = -1
                    self.calcWordLen(r,c,direction)
                    
                elif self.crossword[r,c] == '#':
                    self.total_empty_spaces += 1


        self.empty_spaces_list = np.delete(self.empty_spaces_list, [i for i in range(self.total_word_spaces ,(self.col_size * self.row_size))],None)
        self.total_empty_spaces = (self.col_size * self.row_size) - self.total_empty_spaces

        # INFORMACIO IMPORTANT:    
        # 
        #   el primer [] ens retorna el set de posicio,posibilitat1,posibilitat 2 ex: [0] -> [[0 0],[1 7], [-1 3]]
        #   el segon [] ens retorna: [0] la posicio [0 0] , [1] la posibilitat [1 7], [2] la possiblitat [-1 3]

        if self.debug:
            print 'LVA: '
            print self.empty_spaces_list
            print 'Total lletres per omplir: ',self.total_word_spaces
            print 'Total caselles per omplir: ',self.total_empty_spaces

    ##################################################################################################################################
    '''
    # -> Function that select those words that fill the constraints passed as arguments: 
    
    #   -> op       :   if NOT multiple: op[0] direction, op[1] lenght; if multiple op[0] len right, op[1] len down
    @   -> multiple :   indicates if there's more than one option.
    #   -> pos_x    :   pos x in empty_crossword
    #   -> pos_y    :   pos y in empty_crossword

    # @return a np list of the valid words
    '''
    def itFills(self,word,direction,lenght,pos_x = 0,pos_y = 0):
        
        new_x = pos_x
        new_y = pos_y
        fill = True
       
        try:
            empty = False
            if direction == -1: 
                new_x = pos_x + lenght
                present_letters = np.array(np.asarray([w for w in range(pos_x,new_x) if self.empty_crossword[w,pos_y] != 0]),dtype=object)
                if len(present_letters) == 0 : empty = True

            if direction == 1 :
                new_y = pos_y + lenght
                present_letters = np.array(np.asarray([w for w in range(pos_y,new_y) if self.empty_crossword[pos_x,w] != 0]),dtype=object)                  
                if len(present_letters) == 0 : empty = True
                
        except IndexError:
            pass
        
        esParaula = True
        
        if direction == 1:
            if not empty:
                for word_pos in present_letters:
                    if esParaula:
                        if word[word_pos-pos_y] != self.empty_crossword[pos_x,word_pos]:
                            esParaula = False

        if direction == -1:
            if not empty:
                for word_pos in present_letters:
                    if esParaula:
                        if word[word_pos-pos_x] != self.empty_crossword[word_pos,pos_y]:
                            esParaula = False

        if self.debug:
            
            if esParaula:
                print 'La paraula ',word,' satisfa els requisits.'
            else:
                print 'La paraula ',word,' no satisfa els requisits.' 


        return esParaula

    ##################################################################################################################################
        
    def deleteLastWord(self):
        
        
        if self.last_word[0][3] == 1:
            
            if self.last_word[0][0] < self.col_size:
            
                for i in range (self.last_word[0][1],(self.last_word[0][1] + self.last_word[0][2])):
                    
                    try: 
                        if self.empty_crossword[self.last_word[0][0]+1,i] == 0 or self.empty_crossword[self.last_word[0][0]-1,i] == 0:
                           
                            self.empty_crossword[self.last_word[0][0],i] = 0
                            self.total_empty_spaces += 1
                    except IndexError:
                        pass

            elif self.last_word[0][0] == self.col_size:
                for i in range (self.last_word[0][0],(self.last_word[0][0] + self.last_word[0][2])):
                    
                    try: 
                        if self.empty_crossword[i,self.last_word[0][0]-1] == 0:
                           
                            self.empty_crossword[i,self.last_word[0][0]] = 0
                            self.total_empty_spaces += 1
                    except IndexError:
                        pass
        
        if self.last_word[0][3] == -1:
            if self.last_word[0][1] < self.row_size:
            
                for i in range (self.last_word[0][0],(self.last_word[0][0] + self.last_word[0][2])):
                    
                    try: 
                        if self.empty_crossword[i,self.last_word[0][1]+1] == 0 or self.empty_crossword[i,self.last_word[0][1]-1] == 0:
                           
                            self.empty_crossword[i,self.last_word[0][1]] = 0
                            self.total_empty_spaces += 1
                    except IndexError:
                        pass
            elif self.last_word[0][1] == self.row_size:
                for i in range (self.last_word[0][0],(self.last_word[0][0] + self.last_word[0][2])):
                    
                    try: 
                        if self.empty_crossword[i,self.last_word[0][1]-1] == 0:
                           
                            self.empty_crossword[i,self.last_word[0][1]] = 0
                            self.total_empty_spaces += 1
                    except IndexError:
                        pass
        
                
        del self.last_word[0]
        
        if self.debug:
            print '\n'
            s = [[str(e) if e != 0 else '#' for e in row] for row in self.empty_crossword]
            lens = [max(map(len, col)) for col in zip(*s)]
            fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
            table = [fmt.format(*row) for row in s]
            print '\n'.join(table)
            print '\n'

    ##################################################################################################################################
    
    def insertWord(self, word, options):
        # x,y,len,dir
        
        self.last_word.insert(0,[options[0][0],options[0][1],len(word),options[1][0]])
       
        if (options[1][0] == 1):
            start = options[0][1]
            finish = start + len(word)
            i = 0
            for x in range (start,finish):
                if self.empty_crossword[options[0][0],x] != word[i]:
                    self.total_empty_spaces -= 1

                self.empty_crossword[options[0][0],x] = word[i]
                i+=1
                

        if (options[1][0] == -1):

            start = options[0][0]
            finish = start + len(word)
           
            i = 0
            for x in range (start,finish):
                if self.empty_crossword[x,options[0][1]] != word[i]:
                    self.total_empty_spaces -= 1
                self.empty_crossword[x,options[0][1]] = word[i]
                i+=1
        if self.debug:
            print '\n'
            s = [[str(e) if e != 0 else '#' for e in row] for row in self.empty_crossword]
            lens = [max(map(len, col)) for col in zip(*s)]
            fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
            table = [fmt.format(*row) for row in s]
            print '\n'.join(table)
            print '\n'

    
    ##################################################################################################################################
    
    def getWords(self,lenght):
        return self.dictionary[str(lenght)]

    ##################################################################################################################################
    '''
    # -> Engine 
    #   executes the backtracking algorithm
    # @return a np list of the valid words
    '''
    def backtracking(self,words_not_seen):

        # Proves; posant paraules per quan intentem inserir una paraula, detecti que ja ni ha alguna escrita
        # previament.

        # ----------------------------------------------------------------------------------------------------– #
        
        if not len(words_not_seen) : return self.empty_crossword
        word = words_not_seen[0]     
        words_not_seen = np.delete(words_not_seen,0)
        
        possible_values = self.getWords(word[1][1])

        for word_value in possible_values:
            if self.itFills(word = word_value, direction = word[1][0] ,lenght = word[1][1], pos_x = word[0][0], pos_y = word[0][1]): # satisfa
                self.insertWord(word = word_value, options = word)
                result = self.backtracking(words_not_seen)
                if not self.total_empty_spaces:
                    return result
        
        words_not_seen = np.asarray([word,words_not_seen])
        self.deleteLastWord()

        return None
        
        if self.debug:
            print 'Posicio (',word[0][0],',',word[0][1],') valor al crossword -> (',self.crossword[word[0][0],word[0][1]],') valor al corssword empty ->(',self.empty_crossword[word[0][0],word[0][1]],')'

    ##################################################################################################################################
    '''
    # -> Prints Crossword 
    
    '''
    def printCrossword(self,crossword=None):
        if crossword is None:
            print '\n'
            s = [[str(e) if e != 0 else '#' for e in row] for row in self.empty_crossword]
            lens = [max(map(len, col)) for col in zip(*s)]
            fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
            table = [fmt.format(*row) for row in s]
            print '\n'.join(table)
            print '\n'
       


    ''' Getters '''
    def getDictionary(self):
        return self.dictionary

    def getEmptySpacesList(self):
        return self.empty_spaces_list

    def getCrosswordMatrix(self):
        return self.crossword

    def getEmptyCrossword(self):
        return self.empty_crossword

    def getEmptyIndexPtr(self):
        return self.index_ptr

    def getNumEmptySpaces(self):
        return self.total_empty_spaces


    ''' Program exec '''

if __name__ == '__main__':

    crossword_obj = Crossword(cross_files = crossword_matrix, dict_files = crossword_dic, debug = 0)
    cross = crossword_obj.getCrosswordMatrix()
    empty_spaces_list = crossword_obj.getEmptySpacesList()
    start = time.time()
    if crossword_obj.backtracking(empty_spaces_list) is not None:
        end = time.time()
        crossword_obj.printCrossword()
        print 'Time: ',end-start,' seconds.'
    else:
        print "No s'ha trobat solucio."


    






    
    

  

    
    
   
   
