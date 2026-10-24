package org.apache.logging.log4j;

/** Stub of the Log4j logger. */
public interface Logger {

    void warn(String message, Object... parameters);

    void info(String message, Object... parameters);
}
