# Gaston le Mouton

### What is it ?

The goal of this little software it to easily define an enclosure _E_ and visualise _G(E)_.

### Dependencies

 The GUI is based on pygame, so you must install pygame for your python version. If you have some problems with it, there's a [good solution](https://youtu.be/MdGoAnFP-mU).

### Commands

 * `S` to save the image
 * `G` to make _E = Conv(G(E))_
 * `A` to automatically apply G every second *(on / off)*
 * `Alt + nbr` to save a configuration in the `nbr` slot
 * `nbr` to take back a configuration
 * `T` to generate the Tikz code of the figure *(print + put in clipboard)*
 * `Suppr` to clear the board
 * `left click` to add or delete a point of _E_
 * `right click` to add or delete a marker
 * `Scroll` to change the size of the grid
 * `Escape` to quit
 
### Future developments

 * Make an algorithm with a good complexity to solve *G(E) = F*
 