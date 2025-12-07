# --------------------------------------------------------------------------------------------------
# Pick and Place converter
# --------------------------------------------------------------------------------------------------
# Version 1.0
# Takes standard altium pnp file and converts it into file for juki pnp machine.
# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------


#%%
import csv
import os#
import operator
import glob
import tempfile


# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------

# This is the order that JUKI converter software wants... DON'T change
# "Designator","Footprint","Center-X(mm)","Center-Y(mm)","Rotation","Comment"
#
# This is the order that altium spits out... DON'T change
# "Designator","Comment","Layer","Footprint","Center-X(mm)","Center-Y(mm)","Rotation"

# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
def exitWithPause():
    import atexit, os
    if os.name == 'nt':
      atexit.register(lambda: os.system("pause"))
# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------



# This is possible feilds to find
header = [["Designator",-1],["Footprint",-1],["Center-X(mm)",-1],["Center-Y(mm)",-1],["Rotation",-1],["Comment",0] , ["Layer", -1]]
genPnPFile = "" # New generated file name
csvFiles = [] # List of csv files in current dir
temp = []
topLayer = []
botLayer = []
tmpCSVFile = tempfile.NamedTemporaryFile(delete=False,mode= 'w', newline='')
# Length of standard junk at the front of a pnp file generated from altium
pJLength = len("Pick Place for ")

for csvfile in glob.glob("*.csv"):
  csvFiles.append(csvfile)

for csvList in csvFiles:
  if "Pick Place for " in csvList:
    pnpFileName = csvList
    genPnPFile = pnpFileName[pJLength:]


# ---------------------------------
with open(pnpFileName) as pnpSource:
  pnpReader = csv.reader(pnpSource, delimiter=',')
  # Temp var
  # line = list(pnpReader)[12]

  # # Skip junk in file from altium
  for i in range(13):
    line = pnpReader.__next__()

  # pnpSource.seek(12)
  # line = pnpReader.__next__()

  # Checking line, and removing header to file
  if header[0][0] in line:
    j=0
    k=0
    for hdr in header:
      for element in line:
        if hdr[0] == element:
          header[k][1]=j
          j=0
          break
        j=j+1
      k=k+1

  # ---------------------------------

  # ---------------------------------
  # getting each col positions
  dsg = header[0][1]
  ftprnt = header[1][1]
  cntrX = header[2][1]
  cntrY = header[3][1]
  rotation = header[4][1]
  cmnt = header[5][1]
  lyer = header[6][1]
  # ---------------------------------

  # ---------------------------------
  try:
    # ---------------------------------
    for row in pnpReader:
      if row[ftprnt] == "CC2012-0805":
        row[ftprnt] = "0805"
      temp.append(row)
    # ---------------------------------
  except:
    print("Minor Exception, But can keep going")
  # ---------------------------------
# ---------------------------------


# ---------------------------------
try:
  with tmpCSVFile as O_tmpCSVFile:
    csvWriter = csv.writer(tmpCSVFile)
    csvWriter.writerows(temp)
    tmpCSVFile.close
except:
  print("Error with temp File")
  exitWithPause()
else:
  print("Used temp csv file successfuly")
# ---------------------------------


# ---------------------------------
try:
  # ---------------------------------
  with open(tmpCSVFile.name) as pnpSource:
    pnpReader = csv.reader(pnpSource, delimiter=',')

    # ---------------------------------
    # Finding and replacing footprint names to a standard. This helps for sorting the list
    # It means all the 0805, 0603, ect are in the same spot.
    # Which is less tool changes for running the machine

    # for i in range(12):
    #   pnpReader.__next__()
    # for row in pnpReader:
    #   if row[ftprnt] == "CC2012-0805":
    #     row[ftprnt] = "0805"
    # ---------------------------------


    # Back to the start.
    # pnpSource.seek(0)
    # for i in range(13):
    #   tmp = pnpReader.__next__()

    sortedTemp = sorted(pnpReader,key=operator.itemgetter(1))
    pnp_s = sorted(sortedTemp,key=operator.itemgetter(3))
    # pnp_s = sorted(pnpReader, key=lambda row:(str(row[3]), str(row[1])))


    for row in pnp_s:
      # ------ Designator -------------------
      if dsg != -1:
        if "JP" in row[dsg]:
          continue
        elif "TP" in row[dsg]:
          continue
      # ---------------------------------


      # ----- Footprint ------------------
      if ftprnt != -1:
        row[ftprnt] = row[ftprnt][:12]  # Max 8 Characters Long
        # Remove long not nesseary strings
        if row[ftprnt] == "0402" or row[ftprnt] == "402":
          row[ftprnt] = "4"
        elif row[ftprnt] == "0603" or row[ftprnt] == "603":
          row[ftprnt] = "6"
        elif row[ftprnt] == "0805" or row[ftprnt] == "805":
          row[ftprnt] = "8"
        elif row[ftprnt] == "1206" or row[ftprnt] == "1210":
          row[ftprnt] = "12"
      # ---------------------------------


      # ----- Center-X(mm) ------------------
      # if cntrX != -1:
      # ---------------------------------


      # ----- Center-Y(mm) --------------
      # if cntrY != -1:
      # ---------------------------------


      # ----- Rotation ------------------
      if rotation != -1:
        if row[rotation] == "360":
          row[rotation] = "0"
      # ---------------------------------


      # ----- Comment -------------------
      if cmnt != -1:
        row[cmnt] = row[cmnt][:8]  # Max 8 Characters Long
        if row[cmnt] == "DNL":
          continue
      # ---------------------------------


      # ----- Layer ---------------------
      if lyer != -1:
        if row[lyer] == "TopLayer":
          topLayer.append([row[0]] + [row[4]] + [row[5]] + [row[6]] + [(' '.join([row[1],row[3]]))])
          # topLayer.append(row)
        elif row[lyer] == "BottomLayer":
          botLayer.append([row[0]] + [row[4]] + [row[5]] + [row[6]] + [(' '.join([row[1],row[3]]))])
      else:
        topLayer.append([row[0]] + [row[4]] + [row[5]] + [row[6]] + [(' '.join([row[1],row[3]]))])
      # ---------------------------------

      # newRow.append([row[0]] + [row[3]] + [row[4]] + [row[5]] + [(' '.join([row[1],row[2]]))])
      # pnpWriter.writerow(newRow)

    # -------------- Forloop --------------
  # ---------------------------------
except:
  print("Issue with trying to parse csv p&p file")
  exitWithPause()
else:
  print("Parsed csv file correctly")
# ---------------------------------


try:
  # Write each file (If top and or bot)
  if topLayer:
    # stmp = sorted(topLayer,key=operator.itemgetter(1))
    # pnp_s = sorted(stmp,key=operator.itemgetter(3))
    with open(("TOP_" + genPnPFile), 'w', newline='') as topPnP_Result:
      pnpWriter = csv.writer(topPnP_Result)
      pnpWriter.writerows(topLayer)

  if botLayer:
    with open(("BOT_" + genPnPFile), 'w', newline='') as botPnP_Result:
      pnpWriter = csv.writer(botPnP_Result)
      pnpWriter.writerows(botLayer)

except:
  print("Issue with trying to write new csv p&p files")
  exitWithPause()
else:
  print("Written new csv files correctly")
# ---------------------------------


print("Finished: Happy Picking and Placing!")

exitWithPause()

