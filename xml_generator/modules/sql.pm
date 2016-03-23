package modules::sql;

use strict;

BEGIN {
    our @ISA       = qw( Exporter );
    our @EXPORT_OK = qw(
      getDbh
    
      isTransactionStartedSql
      startTransactionSql
      rollbackSql
      commitSql
      
      lockTablesSql
      unlockTablesSql
      );

    require Exporter;
}

use DBI;
use Error qw(:try);



#===============================================================================
# Database Connection
#===============================================================================

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parse config file and connect to MySQL database
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sub getDbh {
    my $pathConfigFile = shift;
    open( IN, $pathConfigFile ) || die "could not open dbconfig file, $!\n";
    my $configFile = <IN>;
    chomp $configFile;
    my @credentials = split( /,/, $configFile );
    my $dbh = DBI->connect( 'DBI:mysql:' . $credentials[0], $credentials[1], $credentials[2] ) || die "Could not connect to database: $DBI::errstr";
    close IN;

    return $dbh;
}



#===============================================================================
# Transactions
#===============================================================================

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Checks if there's an ongoing transaction
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sub isTransactionStartedSql {
    my $dbh = shift;
    
    return ($dbh->{AutoCommit} == 0);
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Start a transaction
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sub startTransactionSql {
    my $dbh = shift;
    if ( $dbh->{AutoCommit} == 0 ) {
        $dbh->rollback();
        $dbh->{AutoCommit} = 1;
        throw Error::Simple("A transaction is already started.");
    }
    $dbh->{AutoCommit} = 0;
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Cancel the ongoing transaction 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sub rollbackSql {
    my $dbh = shift;
    if ( $dbh->{AutoCommit} == 1 ) {
        throw Error::Simple("No transaction was started before the rollback.");
    }
    $dbh->rollback();
    $dbh->{AutoCommit} = 1;
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Commit a transaction
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sub commitSql {
    my $dbh = shift;

    if ( $dbh->{AutoCommit} == 1 ) {
        throw Error::Simple("No transaction was started before the commit.");
    }
    $dbh->commit();
    $dbh->{AutoCommit} = 1;
}



#===============================================================================
# Tables Lock / Unlock
#===============================================================================

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Locks in the specified mode the tables in the given list
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sub lockTablesSql {
    my $dbh          = shift;
    my $rA_tableList = shift;
    my $mode         = shift;

    my $sth;
    my $query = "LOCK TABLES";
    my $arrayElement;
    for $arrayElement (@$rA_tableList) {
        $query = $query . " $arrayElement $mode,";
    }
    my $parseQuery = $query;
    $parseQuery =~ /^(.+),$/;    #Remove the last ,
    $query = "$1;";
    $sth = MakeQuery( $dbh, $query );
    DestroySth($sth);
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Unlocks all tables locked by this connection
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sub unlockTablesSql {
    my $dbh   = shift;
    my $query = "UNLOCK TABLES;";
    my $sth   = MakeQuery( $dbh, $query );
    DestroySth($sth);
}

1;
