# ProChessing

## Goals and Motivation of the project

* Correctly detect and identify from a visual image through the application of image processing techniques. 
    - a chessboard 
    - configuration of its pieces 
* Such an algorithm could be used to automatically record a game between two players without the need for a digital chess set. 
* In addition, image-based detection of chess pieces is a vital step in building chess-playing robots.

## Major Steps Involved

1. Chessboard Detection 
      - detecting the square pattern to detect each square uniquely. 
      - Perspective Transform ⇾ Canny Edge Detection ⇾ Hough Transform Lines 
2. Classifying each square as occupied or unoccupied 
    - detecting the presence of chess pieces on each square identified from step 1. 
    - A major challenge will be to identify the presence of a piece in a case where the color of the square and the color of the piece kept on it are exactly the same.
3. Identifying the exact piece kept on the particular square. 
    - This will involve classification into different classes (types of pieces on a chessboard) after the segmentation and filtering of the raw images and extracting the image of the piece. 
    - Native Image Processing feature extractors (HOG/ SIFT/Eigen Images) can be used for classification in this step.

