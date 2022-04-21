
def nse( _w, _dataframe, _observed, _simulated) :
    _w.line( 'obssim = pandas.concat( [ %s["%s"].dropna(), %s["%s"].dropna()], axis=1, join="inner")' % ( _dataframe, _observed, _dataframe, _simulated))
    _w.line( 'if len( obssim) == 0 :')
    _w.line( 'nse = None', 1)  ## invalid result
    _w.line( 'else :')
    _w.line( 'obs = obssim["%s"].values' % ( _observed), 1)
    _w.line( 'obs_mean = numpy.mean( obs)', 1)
    _w.line( 'sim = obssim["%s"].values' % ( _simulated), 1)
    _w.line( 'nse = 1.0 - numpy.sum( numpy.square( obs - sim)) / numpy.sum( numpy.square( obs - obs_mean))', 1)
    return 'nse'

def rmse( _w, _dataframe, _observed, _simulated) :
    _w.line( 'obssim = pandas.concat( [ %s["%s"].dropna(), %s["%s"].dropna()], axis=1, join="inner")' % ( _dataframe, _observed, _dataframe, _simulated))
    _w.line( 'if len( obssim) == 0 :')
    _w.line( 'rmse = None', 1)  ## invalid result
    _w.line( 'else :')
    _w.line( 'obs = obssim["%s"].values' % ( _observed), 1)
    _w.line( 'sim = obssim["%s"].values' % ( _simulated), 1)
    _w.line( 'rmse = numpy.sqrt( numpy.mean(numpy.square( sim - obs)) )', 1)
    return 'rmse'

def r2( _w, _dataframe, _observed, _simulated) :
    _w.line( 'obssim = pandas.concat( [ %s["%s"].dropna(), %s["%s"].dropna()], axis=1, join="inner")' % ( _dataframe, _observed, _dataframe, _simulated))
    _w.line( 'if len( obssim) == 0 :')
    _w.line( 'r2 = None', 1)  ## invalid result
    _w.line( 'else :')
    _w.line( 'obs = obssim["%s"].values' % ( _observed), 1)
    _w.line( 'obs_mean = numpy.mean( obs)', 1)
    _w.line( 'sim = obssim["%s"].values' % ( _simulated), 1)

    _w.line( 'n_obs, n_sim = len( obs), len( sim)', 1)
    _w.line( 'assert( n_obs == n_sim)', 1)
    _w.line( 'n = n_obs', 1)

## see http://www.statisticshowto.com/what-is-a-coefficient-of-determination
    _w.line( 'sum_obs = numpy.sum( obs)', 1)
    _w.line( 'sum_sim = numpy.sum( sim)', 1)

    _w.line( 'sum_obs2 = numpy.sum( numpy.square( obs))', 1)
    _w.line( 'sum_sim2 = numpy.sum( numpy.square( sim))', 1)

    _w.line( 'sum_obssim = numpy.sum( obs*sim)', 1)

    _w.line( 'r_denom = math.sqrt( ( n*sum_obs2-( sum_obs*sum_obs)) * ( n*sum_sim2-( sum_sim*sum_sim)))', 1)
    _w.line( 'if abs( r_denom) < 1.0e-12 : ', 1)
    _w.line( 'r = 0.0', 2)
    _w.line( 'else :', 1)
    _w.line( 'r = ( n*sum_obssim - (sum_obs*sum_sim)) / r_denom', 2)
    _w.line( 'r2 = r * r', 1)
    return 'r2'

