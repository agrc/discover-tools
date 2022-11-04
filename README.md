# discover-tools

Random scripts for interacting with Discover

## hexagon_downloader.py

Download 15cm Hexagon imagery with your own quadword.

Builds the proper download links based on a bounding rectangle, downloads the zip files, and then extracts them to a specified folder.

Because each tile's zip file is generated on the fly, this will take a while (hours+ depending on your area). Plan accordingly, and set your area judiciously. The script will estimate the time remaining based on the average time previous tiles have taken.

### Usage

Requires Python 3.7+

Modify the following variables around line 100:

- `quad-word`: The quad-word from your discover links (four words separated by `-`s).
- `out_dir` and `unzip_dir`: Where the downloaded files will be saved and then extracted to.
- `min/max x/y`: min x/y is the top left corner, max x/y is bottom right.

To get the min/max x/y, open your Web Viewer and Downloads link, select Hexagon Downloads, and zoom in until you can see the individual tiles. Choose a spot to be your top left and click on the tile. Hover over the "Download" link to see the x and y in the link (or right click > `Copy Link Address` and paste it in a text editor). The format is `.../15/x/y`. For example, `https://discover.agrc.utah.gov/login/path/your-quad-word-here/footprint/15cm_hexagon_utah/hx/15/6203/12356` has an x value of `6203` and a y value of `12356`. These become your min x/y. Do the same for the bottom right corner to get your max x/y.

Once you've got the right coordinates, save the file and run the script:

`python c:\path\to\where\you\downloaded\hexagon_downloader.py`
