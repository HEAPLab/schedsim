<h1>SchedSim</h1>
<h3>By HeapLab</h3>
<p>This application is a real time schedulers simulator developed using Pythonand PyQt for the GUI.Given  a  set  of  tasks,  which  can  be  defined  in  the  program  and  can  beimported/exported as XML, SchedSim provides as output a list of temporallyordered events, in CSV format, ready to be displayed in a temporal chart.This tool can be useful for simulating new types of schedulers (for researchpurposes for example) and, subsequently, visualize the results starting fromthe ”event list” output file by means of an external application.Output event code is described in the dedicated section.SchedSim provides a simple interface (abstract class) which can be imple-mented to allow user to include his/her own scheduling algorythm.  DeadlineMonotonic algorythm is built-in and provided as a working example.</p>
<p>For further information, design details and UML diagrams please look at the following document:</p>

<object data="docs/SchedSim.pdf" type="application/pdf" width="700px" height="700px">
    <embed src="docs/SchedSim.pdf">
        <p>This browser does not support PDFs. Please download the PDF to view it: <a href="docs/SchedSim.pdf">Download PDF</a>.</p>
    </embed>
</object>
