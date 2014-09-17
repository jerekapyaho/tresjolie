module TresJolie () where
    
import System.Environment
import Data.List

-- Import our own utility library
import Geodesy

main = do
    args <- getArgs
    mapM putStrLn args
