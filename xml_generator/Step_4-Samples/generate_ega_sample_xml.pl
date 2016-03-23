#!/usr/bin/perl

#===============================================================================
# generate_ega_sample_sheet.pl
#
#   Generates an XML document for samples submission to EGA via SRA Webin.
#   Makes use of the mEGAdata database.
#===============================================================================

use strict;
use warnings;
$| = 1;

use DBI;
use Data::Dumper;
use lib '../';
use modules::sql qw(getDbh isTransactionStartedSql startTransactionSql commitSql);

my $testPrefix = "";      #Prefix to add to samples, experiments and run names to allow more than one submission per day on the test server.

my $edccDbPath = "../db_settings.txt";
my $dbh = getDbh($edccDbPath);


#Prepare queries
my $getSampleSth = $dbh->prepare(qq{
    SELECT s.*, d.id AS 'donor_id', d.public_name AS 'donor_name', d.phenotype AS 'phenotype', da.release_status, sp.*
    FROM sample s
    JOIN donor d ON s.donor_id = d.id
    JOIN species sp ON d.taxon_id = sp.taxon_id
    JOIN dataset da ON da.sample_id = s.id AND da.release_status NOT LIKE "R\\_%"
    GROUP BY s.public_name
    ORDER BY s.public_name
});

my $getDonorMetadataSth = $dbh->prepare(qq{
    SELECT dp.property AS 'key', dm.value AS 'value'
    FROM donor_property dp
    LEFT JOIN donor_metadata dm ON dm.donor_property_id = dp.id
    WHERE dm.donor_id = ?
});

my $getSampleMetadataSth = $dbh->prepare(qq{
    SELECT sp.property AS 'key', sm.value AS 'value'
    FROM sample_property sp
    LEFT JOIN sample_metadata sm ON sm.sample_property_id = sp.id
    WHERE sm.sample_id = ?
});




my $sampleXml;

$getSampleSth->execute();
while (my $rH_sample = $getSampleSth->fetchrow_hashref()) {

    my $attributesStr;

    $getDonorMetadataSth->execute($rH_sample->{'donor_id'});
    while (my $rH_meta = $getDonorMetadataSth->fetchrow_hashref()) {
        my $key = $rH_meta->{'key'} || '';
        my $value = $rH_meta->{'value'} || '';
        $attributesStr .= qq{            <SAMPLE_ATTRIBUTE><TAG>$key</TAG><VALUE>$value</VALUE></SAMPLE_ATTRIBUTE>\n};
    }

    $getSampleMetadataSth->execute($rH_sample->{'id'});
    while (my $rH_meta = $getSampleMetadataSth->fetchrow_hashref()) {
        my $key = $rH_meta->{'key'} || '';
        my $value = $rH_meta->{'value'} || '';
        $attributesStr .= qq{            <SAMPLE_ATTRIBUTE><TAG>$key</TAG><VALUE>$value</VALUE></SAMPLE_ATTRIBUTE>\n};
    }

    $sampleXml .= qq{
    <SAMPLE alias="$testPrefix$rH_sample->{public_name}" center_name="MCGILL-EDCC">                     
        <TITLE>$testPrefix$rH_sample->{public_name}</TITLE>
        <SAMPLE_NAME>
            <TAXON_ID>$rH_sample->{taxon_id}</TAXON_ID>
            <SCIENTIFIC_NAME>$rH_sample->{scientific_name}</SCIENTIFIC_NAME>
            <COMMON_NAME>$rH_sample->{common_name}</COMMON_NAME>
        </SAMPLE_NAME>
        <DESCRIPTION>Donor $rH_sample->{donor_name}, Sample $rH_sample->{public_name}</DESCRIPTION>
        <SAMPLE_ATTRIBUTES>
            <SAMPLE_ATTRIBUTE><TAG>Donor ID</TAG><VALUE>$rH_sample->{donor_name}</VALUE></SAMPLE_ATTRIBUTE>
            <SAMPLE_ATTRIBUTE><TAG>Phenotype</TAG><VALUE>$rH_sample->{phenotype}</VALUE></SAMPLE_ATTRIBUTE>
$attributesStr
        </SAMPLE_ATTRIBUTES>
    </SAMPLE>
    };
}

my $xml_str = qq{<SAMPLE_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.sample.xsd">$sampleXml
</SAMPLE_SET>
};

print $xml_str;
print "\n";
