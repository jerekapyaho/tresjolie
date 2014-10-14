This is the [Haskell](http://www.haskell.org) version of tresjolie (very much a work in progress).

Use `ghci` to play around with what's there, like this:

    $ ghci
    GHCi, version 7.6.3: http://www.haskell.org/ghc/  :? for help
    Loading package ghc-prim ... linking ... done.
    Loading package integer-gmp ... linking ... done.
    Loading package base ... linking ... done.
    Prelude> :load Geodesy
    [1 of 1] Compiling Geodesy          ( Geodesy.hs, interpreted )
    Ok, modules loaded: Geodesy.
    *Geodesy> let paris = GeoPt 48.8567 2.3508
    *Geodesy> let berlin = GeoPt 52.5167 13.3833
    *Geodesy> distanceBetween paris berlin 6376.68
    876.8317097528034
    *Geodesy> withinDistance 1000 paris berlin 6376.68
    True
    *Geodesy> withinDistance 500 paris berlin 6376.68
    False

You can also build the project with `runghc` to see the results of the 
smoke test.
