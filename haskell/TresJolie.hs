module TresJolie () where
    
import System.Environment
import Data.List

-- Import our own utility library
import Geodesy

-- Create a GeoPt instance to represent the Tampere Central Square (Keskustori)
tampereCentralSquare = GeoPt { latitude = 61.508056, longitude = 23.768056 }

main = do
    args <- getArgs
    mapM putStrLn args
