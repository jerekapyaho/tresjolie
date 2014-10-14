module Main where
    
import System.Environment
import Data.List
import Network.HTTP
import Network.URI
import Data.Maybe
import System.IO
import Data.Aeson
import Control.Applicative
import qualified Data.ByteString.Lazy.Char8 as BL

-- Import our own utility library
import Geodesy

-- Create a GeoPt instance to represent the Tampere Central Square (Keskustori)
tampereCentralSquare = GeoPt { latitude = 61.508056, longitude = 23.768056 }

data Stop = Stop 
            { name :: String
            , shortName :: String
            }
            
instance FromJSON Stop where
  parseJSON (Object v) = Stop <$> 
                         v .: "name" <*>
                         v .: "shortName"
  parseJSON _          = empty
  
         
{- | Download a URL.  (Left errorMessage) if an error, (Right doc) if success. -}
{- From "Real World Haskell", by Bryan O'Sullivan, John Goerzen, and Don Stewart.
   Copyright 2009 Bryan O'Sullivan, John Goerzen, and Don Stewart, 978-0-596-51498-3. -}
downloadURL :: String -> IO (Either String String)
downloadURL url =
    do resp <- simpleHTTP request
       case resp of
         Left x -> return $ Left ("Error connecting: " ++ show x)
         Right r ->
             case rspCode r of
               (2,_,_) -> return $ Right (rspBody r)
               (3,_,_) -> -- A HTTP redirect
                 case findHeader HdrLocation r of
                   Nothing -> return $ Left (show r)
                   Just url -> downloadURL url
               _ -> return $ Left (show r)
    where request = Request {rqURI = uri,
                             rqMethod = GET,
                             rqHeaders = [],
                             rqBody = ""}
          uri = fromJust $ parseURI url

journeys = "http://data.itsfactory.fi/journeys/api/1/"

main :: IO ()
main = do
    let endpoint = journeys ++ "stop-points"
    json <- downloadURL endpoint
    either handleError doWork json

handleError json = putStrLn "Error reading from Journeys API"
doWork json = 
    do let stops = decode json :: Maybe Stop
       case stops of
         Nothing -> print "Error parsing JSON"
         Just m -> (putStrLn . stop) m
         
stop s = (show . shortName) s ++ " " ++ (show . name) s
