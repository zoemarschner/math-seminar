# Seifert Surface Creator

This program creates and displays the Seifert surface of the projection of the knot drawn by the user, and calculates the Alexander Polynomial and upper and lower bounds for the genus of this knot.

To use the program, run `KnotGenerator.py` in Python. Requires Python 3 with modules `tkinter`, `pyglet`, and `numpy` installed. 

In the drawing program, points must be placed at crossings, but may also be placed in between crossings. You may begin a knot anywhere, but if you do not start at a crossing, press "finish drawing" to smooth the knot. If you do start at a crossing, this will be triggered when you place the fourth line going out of the crossing. Once the knot is smoothed, you will be able to click on crossings to switch them from over to under crossings. Once the knot is as desired, click "output knot" to open a new window displaying the seifert surface of the knot, and the genus and alexander polynomial are printed to standard output. You can continue to draw and output knots while this window is open—they will be opened in additional windows. In the window showing the Seifert surface, press `l` to toggle between light and dark mode, press `b` to toggle between black and white and color mode, and press `w` to write this model to a new file `knot.obj`. To view any .obj file in the same viewer, write `python ObjViewer.py <file>.obj` from the command line.

Created as part of a project for Ithaca High School/Cornell math seminar by Zoë Marschner, Dora Kassabova, and Kasia Fadeeva with mentorship from Hannah Keese.

<sup>Copyright 2019 Zoë Marschner and Dora Kassabova</sup>

