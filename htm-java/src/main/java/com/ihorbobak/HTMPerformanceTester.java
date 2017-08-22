package com.ihorbobak;

import com.opencsv.CSVReader;
import org.joda.time.DateTime;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

import java.io.FileReader;
import java.util.HashMap;
import java.util.Map;

public class HTMPerformanceTester  {
    public static void main(String[] args) {
        String sampleFile = "..\\data\\one_device_2015-2017.csv";
        int batchSize = 100;
        DateTimeFormatter date_format = DateTimeFormat.forPattern("YY-MM-dd HH:mm");

        HTMNetwork htmNetwork = new HTMNetwork("DUMMY");

        long time = System.nanoTime();
        try (CSVReader reader = new CSVReader(new FileReader(sampleFile)))
        {
            int i = 0;
            String[] line;
            while ((line = reader.readNext()) != null) {
                i++;
                String dateGMT = line[11];
                String timeGMT = line[12];
                String sampleMeasurement = line[13];

                DateTime recordDate = DateTime.parse(dateGMT + " " + timeGMT, date_format);
                Double measurement = Double.parseDouble(sampleMeasurement);

                Map<String, Object> m = new HashMap<>();
                m.put("DT", recordDate);
                m.put("Measurement", measurement);
                ResultState res = htmNetwork.compute(m);

                if (res.getAnomaly() > 0.9)
                {
                    System.out.format("DT=%s, M=%.3f, AnomalyScore=%.3f, Error=%.3f, Prediction=%.3f, PredictionNext=%.3f\n",
                            recordDate.toString(date_format), measurement,
                            res.getAnomaly(), res.getError(), res.getPrediction(), res.getPredictionNext()
                    );
                }

                if (i % batchSize == 0) {
                    System.out.format("Processed %d records. The rate is %.1f records/second\n", i, (i * 1000000000.0)/(System.nanoTime() - time));
                }
            }
            System.out.format("Processed %d records. The rate is %.1f records/second\n", i, (i * 1000000000.0)/(System.nanoTime() - time));
        } catch (Exception e) {
            System.out.println(e.getStackTrace());
        }
    }
}

