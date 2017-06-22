# This file is part of EMBL-HLA-Submission.
#
# EMBL-HLA-Submission is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EMBL-HLA-Submission is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with EMBL-HLA-Submission. If not, see <http://www.gnu.org/licenses/>.



import os
from os.path import expanduser

import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
from Tkinter import *

from SubmissionGeneratorIMGT import SubmissionGeneratorIMGT
from AlleleGuiIMGTInputForm import AlleleGuiIMGTInputForm
from AlleleSubCommon import *
#from HLAGene import HLAGene

# The AlleleGui class is an extension of Tkinter.  The GUI elements and interactions are specified in this class.
class AlleleGuiIMGT(Tkinter.Frame):

    # I shouldn't need to write a select-All method but TK is kind of annoying.
    def selectall(self, event):

        event.widget.tag_add("sel","1.0","end")
        
    # Initialize the GUI
    def __init__(self, root):
        Tkinter.Frame.__init__(self, root)
        root.title("An HLA Allele Submission Generator")
        self.parent = root

        # Ctrl-A doesn't work by default in TK.  I guess I need to do it myself.
        root.bind_class("Text","<Control-a>", self.selectall)
        
        # To define the exit behavior.  Save the input sequence text.
        self.parent.protocol('WM_DELETE_WINDOW', self.saveSequenceText)

        button_opt = {'fill': Tkconstants.BOTH, 'padx': 35, 'pady': 5}
        
        
        # A frame for the Instructions Label.
        self.instructionsFrame = Tkinter.Frame(self)  
        self.instructionText = Tkinter.StringVar()       
        self.instructionText.set('\nThis tool will generate an HLA allele submission for\n'
            + 'the IMGT / HLA nucleotide database.\n'
            + 'If you provide login credentials, you may automatically submit the sequence.\n'
            + 'For more information:\n')
        Tkinter.Label(self.instructionsFrame, width=85, height=6, textvariable=self.instructionText).pack()
        self.instructionsFrame.pack()
        
        # Make a frame for the more-info buttons
        self.moreInfoFrame = Tkinter.Frame(self)
        Tkinter.Button(self.moreInfoFrame, text='How to use this tool', command=self.howToUse).grid(row=0, column=0)
        Tkinter.Button(self.moreInfoFrame, text='Example Sequence', command=self.sampleSequence).grid(row=0, column=1)
        self.moreInfoFrame.pack() 
         
         
        # TODO: Can I instruct this text area to fill the space allowed?
        # http://effbot.org/tkinterbook/pack.htm
        
        # Create a frame for the input widget, add scrollbars.
        self.featureInputFrame = Tkinter.Frame(self)
        
        self.featureInstrText = Tkinter.StringVar()
        self.featureInstrText.set('Annotated Sequence:')
        self.featureInstrLabel = Tkinter.Label(self.featureInputFrame, width=80, height=1, textvariable=self.featureInstrText).pack()

        self.featureInputXScrollbar = Scrollbar(self.featureInputFrame, orient=HORIZONTAL)
        self.featureInputXScrollbar.pack(side=BOTTOM, fill=X)

        self.featureInputYScrollbar = Scrollbar(self.featureInputFrame)
        self.featureInputYScrollbar.pack(side=RIGHT, fill=Y)

        self.featureInputGuiObject = Tkinter.Text(
            self.featureInputFrame, width=80, height=12, wrap=NONE
            , xscrollcommand=self.featureInputXScrollbar.set
            , yscrollcommand=self.featureInputYScrollbar.set
        )

        self.featureInputXScrollbar.config(command=self.featureInputGuiObject.xview)
        self.featureInputYScrollbar.config(command=self.featureInputGuiObject.yview) 

        self.featureInputGuiObject.pack() 
        self.featureInputFrame.pack()


        # Create  Frame for "Generate Submission" button.
        self.submButtonFrame = Tkinter.Frame(self)
        Tkinter.Button(self.submButtonFrame, text='Submission Options', command=self.chooseSubmissionOptions).grid(row=0, column=0)
        Tkinter.Button(self.submButtonFrame, text=unichr(8681) + ' Generate an IMGT submission ' + unichr(8681), command=self.constructSubmission).grid(row=0, column=1)
        self.submButtonFrame.pack()

       
        # Output interface is contained on a frame.
        self.submOutputFrame = Tkinter.Frame(self)
        
        self.outputIMGTSubmission = Tkinter.StringVar()
        self.outputIMGTSubmission.set('Allele Submission Preview:')
        self.outputIMGTLabel = Tkinter.Label(self.submOutputFrame, width=80, height=1, textvariable=self.outputIMGTSubmission).pack()

        self.submOutputXScrollbar = Scrollbar(self.submOutputFrame, orient=HORIZONTAL)
        self.submOutputXScrollbar.pack(side=BOTTOM, fill=X)

        self.submOutputYScrollbar = Scrollbar(self.submOutputFrame)
        self.submOutputYScrollbar.pack(side=RIGHT, fill=Y)

        self.submOutputGuiObject = Tkinter.Text(
            self.submOutputFrame, width=80, height=15, wrap=NONE
            , xscrollcommand=self.submOutputXScrollbar.set
            , yscrollcommand=self.submOutputYScrollbar.set
        )

        self.submOutputXScrollbar.config(command=self.submOutputGuiObject.xview)
        self.submOutputYScrollbar.config(command=self.submOutputGuiObject.yview) 

        self.submOutputGuiObject.pack() 
        self.submOutputFrame.pack()

        self.uploadSubmissionFrame = Tkinter.Frame(self)        
        Tkinter.Button(self.uploadSubmissionFrame, text='Upload Submission to IMGT', command=self.saveSubmissionFile).pack(**button_opt)
        Tkinter.Button(self.uploadSubmissionFrame, text='Save Submission to My Computer', command=self.saveSubmissionFile).pack(**button_opt)
        Tkinter.Button(self.uploadSubmissionFrame, text='Exit', command=self.saveSubmissionFile).pack(**button_opt)
        self.uploadSubmissionFrame.pack()
         
    def chooseSubmissionOptions(self):
        print ('Opening the IMGT Submission Options Dialog')
        #emblSubRoot = Tkinter.Tk()
        emblOptionsRoot = Tkinter.Toplevel()
        AlleleGuiIMGTInputForm(emblOptionsRoot).pack()
        #print ('Starting the main loop...')
        emblOptionsRoot.mainloop()

        
    def sampleSequence(self):
        self.featureInputGuiObject.delete('1.0','end')
        self.featureInputGuiObject.insert('1.0', 'aag\nCGTCGT\nccg\nGGCTGA\naat')
        
        assignConfigurationValue("allele_name",'Allele:01:02')
        assignConfigurationValue('gene','HLA-C')
        assignConfigurationValue('sample_id', 'Donor_12345')
        assignConfigurationValue('class','1')
        
        #print ('I just set default values for those mysterious input things')
        
        self.constructSubmission()
        
    # This method should popup some instruction text in a wee window.
    # This should be explicit on how to use the tool.    
    def howToUse(self):
        tkMessageBox.showinfo('How to use this tool',
            'This software is to be used to create an\n'
            + 'IMGT-formatted submission document,\n'
            + 'which specifies a (novel) HLA allele.\n\n'       
                       
            + 'This tool requires you to submit a\n'
            + 'full length HLA allele, including\n'
            + '5\' and 3\' UTRs.\n\n'
            
            + 'Use capital letters for exons,\n'
            + 'lowercase for introns & UTRs.\n\n'
            
            + 'Push the "Example Sequence" button to see a small example of'
            + ' a formatted sequence.\n'
            + 'Sequences should follow this pattern:\n'
            + '5\'utr EX1 int1 EX2 ... EX{X} 3\'utr\n\n'
            
            + 'To use this tool:\n'
            + '1.) Fill in a Sample ID, Gene Name, and Allele.'
            + ' This text will be included in the submission.\n'
            + '2.) Paste your formatted sequence in the\n'
            + 'Annotated Sequence text area.\n'
            + '3.) Push \"Generate an IMGT submission\" button'
            + ' to generate a submission.\n'
            + '4.) Push the "Save the submission" button'
            + ' to store the submission on your computer.\nYou can submit this file to IMGT.\n\n'
            
            + 'All spaces, tabs, and newlines are'
            + ' removed before the nucleotide sequence is translated.'
            )
        
    def contactInformation(self):
        # This method should list contact information for MUMC, and a link to the github page.  
        tkMessageBox.showinfo('Contact Information',
            'This software was created at\n'
            + 'Maastricht University Medical Center\n'
            + 'Transplantation Immunology\n'
            + 'Tissue Typing Laboratory.\n'
            + 'by Ben Matern:\n'
            + 'ben.matern@mumc.nl\n\n'
            
            + 'Please send Ben your bioinformatics\n'
            + 'and data related questions.\n\n'
            
            + 'all other inquiries can be directed\n'
            + 'to Marcel Tilanus:\n'
            + 'm.tilanus@mumc.nl\n\n'
            
            + 'This code will be hosted at:\n'
            + 'https://github.com/transplantation-\nimmunology/EMBL-HLA-Submission\n'
            + 'You will find more information on\n'
            + 'IMGT\'s data format on that page.'

            )

    # Ask user for a output file location, and write the IMGT submission to a file.
    # This takes the input from the output field, rather than generate a new submission.
    # So the user can edit the submission before or after saving it.
    def saveSubmissionFile(self):

        self.dir_opt = options = {}
       
        options['initialdir'] = expanduser("~")
        options['parent'] = self
        options['title'] = 'Specify your output file.'
        options['initialfile'] = 'IMGT.HLA.Submission.txt'
        outputFileObject = tkFileDialog.asksaveasfile(**self.dir_opt)
        submissionText = self.submOutputGuiObject.get('1.0', 'end')
        outputFileObject.write(submissionText)
        
    # Gather sequence information from the input elements, and generate a text IMGT submission.
    def constructSubmission(self):
        try:

            allGen = SubmissionGeneratorIMGT()
            roughFeatureSequence = self.featureInputGuiObject.get('1.0', 'end')
            #allGen.inputSampleID = self.inputSampleID.get()
            #allGen.inputGene = self.inputGene.get()
            #allGen.inputAllele = self.inputAllele.get()
            allGen.inputSampleID = getConfigurationValue('sample_id')
            allGen.inputGene = getConfigurationValue('gene')
            allGen.inputAllele = getConfigurationValue('allele_name')
            
            
            
            allGen.processInputSequence(roughFeatureSequence)
            enaSubmission = allGen.buildENASubmission()
            self.submOutputGuiObject.delete('1.0','end')    
            self.submOutputGuiObject.insert('1.0', enaSubmission) 
            
        except KeyError, e:
            tkMessageBox.showerror('Missing Submission Options'
                ,'You are missing some required information.\n'
                + 'Use the \'Submission Options\' button.\n'
                + 'Missing Data: ' + str(e))
            
    def saveSequenceText(self):
        assignConfigurationValue('sequence', self.featureInputGuiObject.get('1.0', 'end'))
        
            

