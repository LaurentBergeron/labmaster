/******************************************************************************
 *                                                                         
 * Copyright Keysight Technologies  2011-2015.
 *
 *****************************************************************************/

#ifndef __AGM8190_HEADER
#define __AGM8190_HEADER

#include <ivivisatype.h>

#if defined(__cplusplus) || defined(__cplusplus__)
extern "C" {
#endif

/**************************************************************************** 
 *---------------------------- Attribute Defines ---------------------------* 
 ****************************************************************************/
#ifndef IVI_ATTR_BASE
#define IVI_ATTR_BASE                 1000000
#endif

#ifndef IVI_INHERENT_ATTR_BASE		        
#define IVI_INHERENT_ATTR_BASE        (IVI_ATTR_BASE +  50000)   /* base for inherent capability attributes */
#endif

#ifndef IVI_CLASS_ATTR_BASE           
#define IVI_CLASS_ATTR_BASE           (IVI_ATTR_BASE + 250000)   /* base for IVI-defined class attributes */
#endif

#ifndef IVI_LXISYNC_ATTR_BASE         
#define IVI_LXISYNC_ATTR_BASE         (IVI_ATTR_BASE + 950000)   /* base for IviLxiSync attributes */
#endif

#ifndef IVI_SPECIFIC_ATTR_BASE        
#define IVI_SPECIFIC_ATTR_BASE        (IVI_ATTR_BASE + 150000)   /* base for attributes of specific drivers */
#endif


/*===== IVI Inherent Instrument Attributes ==============================*/    

/*- Driver Identification */

#define AGM8190_ATTR_SPECIFIC_DRIVER_DESCRIPTION              (IVI_INHERENT_ATTR_BASE + 514L)  /* ViString, read-only */
#define AGM8190_ATTR_SPECIFIC_DRIVER_PREFIX                   (IVI_INHERENT_ATTR_BASE + 302L)  /* ViString, read-only */
#define AGM8190_ATTR_SPECIFIC_DRIVER_VENDOR                   (IVI_INHERENT_ATTR_BASE + 513L)  /* ViString, read-only */
#define AGM8190_ATTR_SPECIFIC_DRIVER_REVISION                 (IVI_INHERENT_ATTR_BASE + 551L)  /* ViString, read-only */
#define AGM8190_ATTR_SPECIFIC_DRIVER_CLASS_SPEC_MAJOR_VERSION (IVI_INHERENT_ATTR_BASE + 515L)  /* ViInt32, read-only */
#define AGM8190_ATTR_SPECIFIC_DRIVER_CLASS_SPEC_MINOR_VERSION (IVI_INHERENT_ATTR_BASE + 516L)  /* ViInt32, read-only */

/*- User Options */

#define AGM8190_ATTR_RANGE_CHECK                            (IVI_INHERENT_ATTR_BASE + 2L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_QUERY_INSTRUMENT_STATUS                (IVI_INHERENT_ATTR_BASE + 3L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_CACHE                                  (IVI_INHERENT_ATTR_BASE + 4L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_SIMULATE                               (IVI_INHERENT_ATTR_BASE + 5L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_RECORD_COERCIONS                       (IVI_INHERENT_ATTR_BASE + 6L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_INTERCHANGE_CHECK                      (IVI_INHERENT_ATTR_BASE + 21L)  /* ViBoolean, read-write */

/*- Advanced Session Information */

#define AGM8190_ATTR_LOGICAL_NAME                           (IVI_INHERENT_ATTR_BASE + 305L)  /* ViString, read-only */
#define AGM8190_ATTR_IO_RESOURCE_DESCRIPTOR                 (IVI_INHERENT_ATTR_BASE + 304L)  /* ViString, read-only */
#define AGM8190_ATTR_DRIVER_SETUP                           (IVI_INHERENT_ATTR_BASE + 7L)  /* ViString, read-only */

/*- Driver Capabilities */

#define AGM8190_ATTR_GROUP_CAPABILITIES                     (IVI_INHERENT_ATTR_BASE + 401L)  /* ViString, read-only */
#define AGM8190_ATTR_SUPPORTED_INSTRUMENT_MODELS            (IVI_INHERENT_ATTR_BASE + 327L)  /* ViString, read-only */

/*- Instrument Identification */

#define AGM8190_ATTR_INSTRUMENT_FIRMWARE_REVISION           (IVI_INHERENT_ATTR_BASE + 510L)  /* ViString, read-only */
#define AGM8190_ATTR_INSTRUMENT_MANUFACTURER                (IVI_INHERENT_ATTR_BASE + 511L)  /* ViString, read-only */
#define AGM8190_ATTR_INSTRUMENT_MODEL                       (IVI_INHERENT_ATTR_BASE + 512L)  /* ViString, read-only */


/*===== Instrument-Specific Attributes =====================================*/

/*- Arbitrary */

#define AGM8190_ATTR_ARB_GAIN                               (IVI_CLASS_ATTR_BASE + 202L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARB_OFFSET                             (IVI_CLASS_ATTR_BASE + 203L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARB_SAMPLE_RATE                        (IVI_CLASS_ATTR_BASE + 204L)  /* ViReal64, read-write */

/*- Waveform */

#define AGM8190_ATTR_ARB_WAVEFORM_HANDLE                    (IVI_CLASS_ATTR_BASE + 201L)  /* ViInt32, read-write */
#define AGM8190_ATTR_MAX_NUM_WAVEFORMS                      (IVI_CLASS_ATTR_BASE + 205L)  /* ViInt32, read-only */
#define AGM8190_ATTR_WAVEFORM_QUANTUM                       (IVI_CLASS_ATTR_BASE + 206L)  /* ViInt32, read-only */
#define AGM8190_ATTR_MAX_WAVEFORM_SIZE                      (IVI_CLASS_ATTR_BASE + 208L)  /* ViInt32, read-only */
#define AGM8190_ATTR_MIN_WAVEFORM_SIZE                      (IVI_CLASS_ATTR_BASE + 207L)  /* ViInt32, read-only */

/*- Sequence */

#define AGM8190_ATTR_ARB_SEQUENCE_HANDLE                    (IVI_CLASS_ATTR_BASE + 211L)  /* ViInt32, read-write */
#define AGM8190_ATTR_MAX_SEQUENCE_LENGTH                    (IVI_CLASS_ATTR_BASE + 214L)  /* ViInt32, read-only */
#define AGM8190_ATTR_MIN_SEQUENCE_LENGTH                    (IVI_CLASS_ATTR_BASE + 213L)  /* ViInt32, read-only */
#define AGM8190_ATTR_MAX_LOOP_COUNT                         (IVI_CLASS_ATTR_BASE + 215L)  /* ViInt32, read-only */
#define AGM8190_ATTR_MAX_NUM_SEQUENCES                      (IVI_CLASS_ATTR_BASE + 212L)  /* ViInt32, read-only */

/*- Output */

#define AGM8190_ATTR_CHANNEL_COUNT                          (IVI_INHERENT_ATTR_BASE + 203L)  /* ViInt32, read-only */
#define AGM8190_ATTR_OUTPUT_ENABLED                         (IVI_CLASS_ATTR_BASE + 3L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_OUTPUT_MODE                            (IVI_CLASS_ATTR_BASE + 1L)  /* ViInt32, read-write */
#define AGM8190_ATTR_REF_CLOCK_SOURCE                       (IVI_CLASS_ATTR_BASE + 2L)  /* ViInt32, read-write */

/*- Trigger */

#define AGM8190_ATTR_INTERNAL_TRIGGER_RATE                  (IVI_CLASS_ATTR_BASE + 310L)  /* ViReal64, read-write */
#define AGM8190_ATTR_TRIGGER_SOURCE                         (IVI_CLASS_ATTR_BASE + 302L)  /* ViInt32, read-write */

/*- Output */

#define AGM8190_ATTR_OUTPUT_CHANNEL_DELAY                          (IVI_SPECIFIC_ATTR_BASE + 1L)  /* ViReal64, read-write */
#define AGM8190_ATTR_OUTPUT_CHANNEL_DC_VOLTAGE_TERMINATION         (IVI_SPECIFIC_ATTR_BASE + 18L)  /* ViReal64, read-write */
#define AGM8190_ATTR_OUTPUT_ROUTE                                  (IVI_SPECIFIC_ATTR_BASE + 20L)  /* ViInt32, read-write */
#define AGM8190_ATTR_OUTPUT_COMPLEMENT_ENABLED                     (IVI_SPECIFIC_ATTR_BASE + 40L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE                 (IVI_SPECIFIC_ATTR_BASE + 52L)  /* ViInt32, read-write */
#define AGM8190_ATTR_OUTPUT_DIFFERENTIAL_OFFSET                    (IVI_SPECIFIC_ATTR_BASE + 58L)  /* ViInt32, read-write */
#define AGM8190_ATTR_OUTPUT_CHANNEL_COARSE_DELAY                   (IVI_SPECIFIC_ATTR_BASE + 59L)  /* ViReal64, read-write */
#define AGM8190_ATTR_OUTPUT_EXTERNAL_REFERENCE_CLOCK_FREQUENCY     (IVI_SPECIFIC_ATTR_BASE + 56L)  /* ViReal64, read-write */
#define AGM8190_ATTR_OUTPUT_DIFFERENTIAL_OFFSET_MAX                (IVI_SPECIFIC_ATTR_BASE + 108L)  /* ViInt32, read-only */
#define AGM8190_ATTR_OUTPUT_DIFFERENTIAL_OFFSET_MIN                (IVI_SPECIFIC_ATTR_BASE + 109L)  /* ViInt32, read-only */
#define AGM8190_ATTR_OUTPUT_EXTERNAL_REFERENCE_CLOCK_FREQUENCY_MAX (IVI_SPECIFIC_ATTR_BASE + 110L)  /* ViReal64, read-only */
#define AGM8190_ATTR_OUTPUT_EXTERNAL_REFERENCE_CLOCK_FREQUENCY_MIN (IVI_SPECIFIC_ATTR_BASE + 111L)  /* ViReal64, read-only */
#define AGM8190_ATTR_OUTPUT_CHANNEL_DC_VOLTAGE_TERMINATION_MIN     (IVI_SPECIFIC_ATTR_BASE + 123L)  /* ViReal64, read-only */
#define AGM8190_ATTR_OUTPUT_CHANNEL_DC_VOLTAGE_TERMINATION_MAX     (IVI_SPECIFIC_ATTR_BASE + 124L)  /* ViReal64, read-only */
#define AGM8190_ATTR_OUTPUT_CHANNEL_COARSE_DELAY_MIN               (IVI_SPECIFIC_ATTR_BASE + 125L)  /* ViReal64, read-only */
#define AGM8190_ATTR_OUTPUT_CHANNEL_COARSE_DELAY_MAX               (IVI_SPECIFIC_ATTR_BASE + 126L)  /* ViReal64, read-only */
#define AGM8190_ATTR_OUTPUT_CHANNEL_DELAY_MIN                      (IVI_SPECIFIC_ATTR_BASE + 127L)  /* ViReal64, read-only */
#define AGM8190_ATTR_OUTPUT_CHANNEL_DELAY_MAX                      (IVI_SPECIFIC_ATTR_BASE + 128L)  /* ViReal64, read-only */
#define AGM8190_ATTR_OUTPUT_REDUCED_NOISE_FLOOR_ENABLED            (IVI_SPECIFIC_ATTR_BASE + 157L)  /* ViBoolean, read-write */

/*- SampleClock */

#define AGM8190_ATTR_SAMPLE_CLOCK_OUTPUT                    (IVI_SPECIFIC_ATTR_BASE + 57L)  /* ViInt32, read-write */

/*- Arbitrary */

#define AGM8190_ATTR_ARBITRARY_AMPLITUDE                    (IVI_SPECIFIC_ATTR_BASE + 4L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_OFFSET                       (IVI_SPECIFIC_ATTR_BASE + 5L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_SAMPLE_RATE                  (IVI_SPECIFIC_ATTR_BASE + 6L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_SAMPLE_RATE_EXTERNAL         (IVI_SPECIFIC_ATTR_BASE + 14L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_BINARY_ALIGNMENT             (IVI_SPECIFIC_ATTR_BASE + 15L)  /* ViInt32, read-only */
#define AGM8190_ATTR_ARBITRARY_SAMPLE_BIT_RESOLUTION        (IVI_SPECIFIC_ATTR_BASE + 16L)  /* ViInt32, read-only */
#define AGM8190_ATTR_ARBITRARY_BIT_RESOLUTION_MODE          (IVI_SPECIFIC_ATTR_BASE + 21L)  /* ViInt32, read-write */
#define AGM8190_ATTR_ARBITRARY_DAC_FORMAT                   (IVI_SPECIFIC_ATTR_BASE + 26L)  /* ViInt32, read-write */
#define AGM8190_ATTR_ARBITRARY_DAC_AMPLITUDE                (IVI_SPECIFIC_ATTR_BASE + 27L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_DAC_OFFSET                   (IVI_SPECIFIC_ATTR_BASE + 28L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_AC_AMPLITUDE                 (IVI_SPECIFIC_ATTR_BASE + 29L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_DC_OFFSET                    (IVI_SPECIFIC_ATTR_BASE + 30L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_DC_AMPLITUDE                 (IVI_SPECIFIC_ATTR_BASE + 31L)  /* ViReal64, read-write */
#define AGM8190_ATTR_ARBITRARY_SEQUENCING_MODE              (IVI_SPECIFIC_ATTR_BASE + 49L)  /* ViInt32, read-write */
#define AGM8190_ATTR_ARBITRARY_DC_FORMAT                    (IVI_SPECIFIC_ATTR_BASE + 60L)  /* ViInt32, read-write */
#define AGM8190_ATTR_ARBITRARY_AC_FORMAT                    (IVI_SPECIFIC_ATTR_BASE + 61L)  /* ViInt32, read-write */
#define AGM8190_ATTR_ARBITRARY_AC_AMPLITUDE_MAX             (IVI_SPECIFIC_ATTR_BASE + 76L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_AC_AMPLITUDE_MIN             (IVI_SPECIFIC_ATTR_BASE + 77L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_DAC_AMPLITUDE_MAX            (IVI_SPECIFIC_ATTR_BASE + 78L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_DAC_AMPLITUDE_MIN            (IVI_SPECIFIC_ATTR_BASE + 79L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_DAC_OFFSET_MAX               (IVI_SPECIFIC_ATTR_BASE + 80L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_DAC_OFFSET_MIN               (IVI_SPECIFIC_ATTR_BASE + 81L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_DC_AMPLITUDE_MAX             (IVI_SPECIFIC_ATTR_BASE + 82L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_DC_AMPLITUDE_MIN             (IVI_SPECIFIC_ATTR_BASE + 83L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_DC_OFFSET_MAX                (IVI_SPECIFIC_ATTR_BASE + 84L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_DC_OFFSET_MIN                (IVI_SPECIFIC_ATTR_BASE + 85L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_AMPLITUDE_MAX                (IVI_SPECIFIC_ATTR_BASE + 86L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_AMPLITUDE_MIN                (IVI_SPECIFIC_ATTR_BASE + 87L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_OFFSET_MAX                   (IVI_SPECIFIC_ATTR_BASE + 88L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_OFFSET_MIN                   (IVI_SPECIFIC_ATTR_BASE + 89L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_SAMPLE_RATE_MAX              (IVI_SPECIFIC_ATTR_BASE + 90L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_SAMPLE_RATE_MIN              (IVI_SPECIFIC_ATTR_BASE + 91L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_SAMPLE_RATE_EXTERNAL_MAX     (IVI_SPECIFIC_ATTR_BASE + 92L)  /* ViReal64, read-only */
#define AGM8190_ATTR_ARBITRARY_SAMPLE_RATE_EXTERNAL_MIN     (IVI_SPECIFIC_ATTR_BASE + 93L)  /* ViReal64, read-only */

/*- Waveform */

#define AGM8190_ATTR_WAVEFORM_NUMBER_WAVEFORMS_MAX          (IVI_SPECIFIC_ATTR_BASE + 7L)  /* ViInt32, read-only */
#define AGM8190_ATTR_CHANNEL_WAVEFORM_QUANTUM               (IVI_SPECIFIC_ATTR_BASE + 8L)  /* ViInt32, read-only */
#define AGM8190_ATTR_WAVEFORM_SIZE_MAX_64                   (IVI_SPECIFIC_ATTR_BASE + 9L)  /* ViInt64, read-only */
#define AGM8190_ATTR_WAVEFORM_SIZE_MIN_64                   (IVI_SPECIFIC_ATTR_BASE + 10L)  /* ViInt64, read-only */
#define AGM8190_ATTR_WAVEFORM_ACTIVE_SEGMENT                (IVI_SPECIFIC_ATTR_BASE + 47L)  /* ViInt32, read-write */
#define AGM8190_ATTR_WAVEFORM_QUERY_CATALOG                 (IVI_SPECIFIC_ATTR_BASE + 48L)  /* ViString, read-only */
#define AGM8190_ATTR_WAVEFORM_DYNAMIC_SELECT_MODE           (IVI_SPECIFIC_ATTR_BASE + 50L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_WAVEFORM_VALID_BIT_WIDTH               (IVI_SPECIFIC_ATTR_BASE + 51L)  /* ViInt32, read-write */
#define AGM8190_ATTR_WAVEFORM_ADVANCEMENT_MODE              (IVI_SPECIFIC_ATTR_BASE + 120L)  /* ViInt32, read-write */
#define AGM8190_ATTR_WAVEFORM_LOOP_COUNT                    (IVI_SPECIFIC_ATTR_BASE + 121L)  /* ViInt64, read-write */
#define AGM8190_ATTR_WAVEFORM_MARKER_ENABLED                (IVI_SPECIFIC_ATTR_BASE + 122L)  /* ViBoolean, read-write */

/*- Sequence */

#define AGM8190_ATTR_SEQUENCE_ACTIVE_SEQUENCE                      (IVI_SPECIFIC_ATTR_BASE + 62L)  /* ViInt32, read-write */
#define AGM8190_ATTR_SEQUENCE_LENGTH_MAX                           (IVI_SPECIFIC_ATTR_BASE + 67L)  /* ViInt32, read-only */
#define AGM8190_ATTR_SEQUENCE_LENGTH_MIN                           (IVI_SPECIFIC_ATTR_BASE + 68L)  /* ViInt32, read-only */
#define AGM8190_ATTR_SEQUENCE_NUMBER_SEQUENCES_MAX                 (IVI_SPECIFIC_ATTR_BASE + 69L)  /* ViInt32, read-only */
#define AGM8190_ATTR_SEQUENCE_LOOP_COUNT_MAX                       (IVI_SPECIFIC_ATTR_BASE + 70L)  /* ViInt64, read-only */
#define AGM8190_ATTR_SEQUENCE_DYNAMIC_MODE_ENABLED                 (IVI_SPECIFIC_ATTR_BASE + 71L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_SEQUENCE_ACTIVE_DYNAMIC_SEQUENCE              (IVI_SPECIFIC_ATTR_BASE + 72L)  /* ViInt32, read-write */
#define AGM8190_ATTR_SEQUENCE_QUERY_CATALOG                        (IVI_SPECIFIC_ATTR_BASE + 112L)  /* ViString, read-only */
#define AGM8190_ATTR_SEQUENCE_DYNAMIC_PORT_HARDWARE_INPUT_DISABLED (IVI_SPECIFIC_ATTR_BASE + 138L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_SEQUENCE_STREAMING_ENABLED                    (IVI_SPECIFIC_ATTR_BASE + 152L)  /* ViBoolean, read-write */

/*- SequenceTable */

#define AGM8190_ATTR_SEQUENCE_STATE                         (IVI_SPECIFIC_ATTR_BASE + 153L)  /* ViInt32, read-only */

/*- Scenario */

#define AGM8190_ATTR_SCENARIO_START_INDEX                   (IVI_SPECIFIC_ATTR_BASE + 73L)  /* ViInt32, read-write */
#define AGM8190_ATTR_SCENARIO_ADVANCEMENT_MODE              (IVI_SPECIFIC_ATTR_BASE + 74L)  /* ViInt32, read-write */
#define AGM8190_ATTR_SCENARIO_LOOP_COUNT                    (IVI_SPECIFIC_ATTR_BASE + 75L)  /* ViInt64, read-write */

/*- DigitalUpConversion */

#define AGM8190_ATTR_DIGITIAL_UP_CONVERSION_CARRIER_AMPLITUDE_SCALE     (IVI_SPECIFIC_ATTR_BASE + 143L)  /* ViReal64, read-write */
#define AGM8190_ATTR_DIGITIAL_UP_CONVERSION_CARRIER_AMPLITUDE_SCALE_MIN (IVI_SPECIFIC_ATTR_BASE + 144L)  /* ViReal64, read-only */
#define AGM8190_ATTR_DIGITIAL_UP_CONVERSION_CARRIER_AMPLITUDE_SCALE_MAX (IVI_SPECIFIC_ATTR_BASE + 145L)  /* ViReal64, read-only */
#define AGM8190_ATTR_CARRIER_PHASE_OFFSET                               (IVI_SPECIFIC_ATTR_BASE + 149L)  /* ViReal64, read-write */
#define AGM8190_ATTR_CARRIER_PHASE_OFFSET_MAX                           (IVI_SPECIFIC_ATTR_BASE + 150L)  /* ViReal64, read-only */
#define AGM8190_ATTR_CARRIER_PHASE_OFFSET_MIN                           (IVI_SPECIFIC_ATTR_BASE + 151L)  /* ViReal64, read-only */

/*- System */

#define AGM8190_ATTR_SYSTEM_SERIAL_NUMBER                   (IVI_SPECIFIC_ATTR_BASE + 12L)  /* ViString, read-only */
#define AGM8190_ATTR_SYSTEM_OPTIONS_INSTALLED               (IVI_SPECIFIC_ATTR_BASE + 41L)  /* ViString, read-only */
#define AGM8190_ATTR_SYSTEM_TIMEOUT_MILLISECONDS            (IVI_SPECIFIC_ATTR_BASE + 131L)  /* ViInt32, read-write */
#define AGM8190_ATTR_SYSTEM_TRACE_ENABLED                   (IVI_SPECIFIC_ATTR_BASE + 132L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_SYSTEM_LICENSES_INSTALLED              (IVI_SPECIFIC_ATTR_BASE + 137L)  /* ViString, read-only */

/*- Instrument */

#define AGM8190_ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED    (IVI_SPECIFIC_ATTR_BASE + 19L)  /* ViInt32, read-write */
#define AGM8190_ATTR_INSTRUMENT_SLOT_NUMBER                 (IVI_SPECIFIC_ATTR_BASE + 116L)  /* ViInt32, read-only */
#define AGM8190_ATTR_MULTI_MODULE_CONFIG_ENABLED            (IVI_SPECIFIC_ATTR_BASE + 154L)  /* ViBoolean, read-only */
#define AGM8190_ATTR_MULTI_MODULE_MODE                      (IVI_SPECIFIC_ATTR_BASE + 155L)  /* ViInt32, read-only */

/*- Marker */

#define AGM8190_ATTR_MARKER_SYNC_MARKER_AMPLITUDE           (IVI_SPECIFIC_ATTR_BASE + 22L)  /* ViReal64, read-write */
#define AGM8190_ATTR_MARKER_SYNC_MARKER_OFFSET              (IVI_SPECIFIC_ATTR_BASE + 23L)  /* ViReal64, read-write */
#define AGM8190_ATTR_MARKER_SAMPLE_MARKER_AMPLITUDE         (IVI_SPECIFIC_ATTR_BASE + 24L)  /* ViReal64, read-write */
#define AGM8190_ATTR_MARKER_SAMPLE_MARKER_OFFSET            (IVI_SPECIFIC_ATTR_BASE + 25L)  /* ViReal64, read-write */
#define AGM8190_ATTR_MARKER_SAMPLE_MARKER_AMPLITUDE_MAX     (IVI_SPECIFIC_ATTR_BASE + 100L)  /* ViReal64, read-only */
#define AGM8190_ATTR_MARKER_SAMPLE_MARKER_AMPLITUDE_MIN     (IVI_SPECIFIC_ATTR_BASE + 101L)  /* ViReal64, read-only */
#define AGM8190_ATTR_MARKER_SAMPLE_MARKER_OFFSET_MAX        (IVI_SPECIFIC_ATTR_BASE + 102L)  /* ViReal64, read-only */
#define AGM8190_ATTR_MARKER_SAMPLE_MARKER_OFFSET_MIN        (IVI_SPECIFIC_ATTR_BASE + 103L)  /* ViReal64, read-only */
#define AGM8190_ATTR_MARKER_SYNC_MARKER_AMPLITUDE_MAX       (IVI_SPECIFIC_ATTR_BASE + 104L)  /* ViReal64, read-only */
#define AGM8190_ATTR_MARKER_SYNC_MARKER_AMPLITUDE_MIN       (IVI_SPECIFIC_ATTR_BASE + 105L)  /* ViReal64, read-only */
#define AGM8190_ATTR_MARKER_SYNC_MARKER_OFFSET_MAX          (IVI_SPECIFIC_ATTR_BASE + 106L)  /* ViReal64, read-only */
#define AGM8190_ATTR_MARKER_SYNC_MARKER_OFFSET_MIN          (IVI_SPECIFIC_ATTR_BASE + 107L)  /* ViReal64, read-only */

/*- Trigger */

#define AGM8190_ATTR_TRIGGER_THRESHOLD                            (IVI_SPECIFIC_ATTR_BASE + 32L)  /* ViReal64, read-write */
#define AGM8190_ATTR_TRIGGER_IMPEDANCE                            (IVI_SPECIFIC_ATTR_BASE + 33L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_SLOPE                                (IVI_SPECIFIC_ATTR_BASE + 34L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_EVENT_IMPEDANCE                      (IVI_SPECIFIC_ATTR_BASE + 35L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_EVENT_SLOPE                          (IVI_SPECIFIC_ATTR_BASE + 36L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_EVENT_THRESHOLD                      (IVI_SPECIFIC_ATTR_BASE + 37L)  /* ViReal64, read-write */
#define AGM8190_ATTR_TRIGGER_EVENT_THRESHOLD_MAX                  (IVI_SPECIFIC_ATTR_BASE + 94L)  /* ViReal64, read-only */
#define AGM8190_ATTR_TRIGGER_EVENT_THRESHOLD_MIN                  (IVI_SPECIFIC_ATTR_BASE + 95L)  /* ViReal64, read-only */
#define AGM8190_ATTR_TRIGGER_INTERNAL_RATE_MAX                    (IVI_SPECIFIC_ATTR_BASE + 96L)  /* ViReal64, read-only */
#define AGM8190_ATTR_TRIGGER_INTERNAL_RATE_MIN                    (IVI_SPECIFIC_ATTR_BASE + 97L)  /* ViReal64, read-only */
#define AGM8190_ATTR_TRIGGER_THRESHOLD_MAX                        (IVI_SPECIFIC_ATTR_BASE + 98L)  /* ViReal64, read-only */
#define AGM8190_ATTR_TRIGGER_THRESHOLD_MIN                        (IVI_SPECIFIC_ATTR_BASE + 99L)  /* ViReal64, read-only */
#define AGM8190_ATTR_TRIGGER_ENABLE_EVENT_SOURCE                  (IVI_SPECIFIC_ATTR_BASE + 113L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_ADVANCEMENT_EVENT_SOURCE             (IVI_SPECIFIC_ATTR_BASE + 114L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_IS_GATE_OPEN                         (IVI_SPECIFIC_ATTR_BASE + 115L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_TRIGGER_ARM_MODE                             (IVI_SPECIFIC_ATTR_BASE + 134L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_GATE_MODE                            (IVI_SPECIFIC_ATTR_BASE + 135L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_MODE                                 (IVI_SPECIFIC_ATTR_BASE + 136L)  /* ViInt32, read-write */
#define AGM8190_ATTR_TRIGGER_ENABLE_EVENT_HARDWARE_INPUT_DISABLED (IVI_SPECIFIC_ATTR_BASE + 146L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_TRIGGER_HARDWARE_INPUT_DISABLED              (IVI_SPECIFIC_ATTR_BASE + 147L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_TRIGGER_ADVANCEMENT_HARDWARE_INPUT_DISABLED  (IVI_SPECIFIC_ATTR_BASE + 148L)  /* ViBoolean, read-write */
#define AGM8190_ATTR_ADVANCEMENT_EVENT_SOURCE_EX                  (IVI_SPECIFIC_ATTR_BASE + 159L)  /* ViInt32, read-write */

/*- Status */

#define AGM8190_ATTR_STATUS_SEQUENCE_DATA_OK                (IVI_SPECIFIC_ATTR_BASE + 129L)  /* ViBoolean, read-only */
#define AGM8190_ATTR_STATUS_SEQUENCE_LINEAR_PLAYTIME_OK     (IVI_SPECIFIC_ATTR_BASE + 130L)  /* ViBoolean, read-only */
#define AGM8190_ATTR_STATUS_SERIAL_POLL                     (IVI_SPECIFIC_ATTR_BASE + 133L)  /* ViInt32, read-only */
#define AGM8190_ATTR_STATUS_SEQUENCE_STREAMING_DATA_OK      (IVI_SPECIFIC_ATTR_BASE + 158L)  /* ViBoolean, read-only */

/*- Memory */

#define AGM8190_ATTR_MEMORY_CURRENT_FOLDER                  (IVI_SPECIFIC_ATTR_BASE + 117L)  /* ViString, read-write */


/**************************************************************************** 
 *------------------------ Attribute Value Defines -------------------------* 
 ****************************************************************************/

/*- Defined values for 
	attribute AGM8190_ATTR_OUTPUT_MODE
	parameter OutputMode in function AgM8190_ConfigureOutputMode */

#define AGM8190_VAL_OUTPUT_ARB                              1
#define AGM8190_VAL_OUTPUT_SEQ                              2

/*- Defined values for 
	attribute AGM8190_ATTR_REF_CLOCK_SOURCE
	parameter Source in function AgM8190_ConfigureRefClockSource */

#define AGM8190_VAL_REF_CLOCK_INTERNAL                      0
#define AGM8190_VAL_REF_CLOCK_EXTERNAL                      1

/*- Defined values for 
	attribute AGM8190_ATTR_TRIGGER_SOURCE
	parameter Source in function AgM8190_ConfigureTriggerSource */

#define AGM8190_VAL_EXTERNAL                                1
#define AGM8190_VAL_INTERNAL_TRIGGER                        3

/*- Defined values for 
	parameter SampleClockSource in function AgM8190_SampleClockGetSampleClockSource
	parameter SampleClockSource in function AgM8190_SampleClockSetSampleClockSource
	parameter Source in function AgM8190_SampleClockConfigure */

#define AGM8190_VAL_SAMPLE_CLOCK_SOURCE_INTERNAL            0
#define AGM8190_VAL_SAMPLE_CLOCK_SOURCE_EXTERNAL            1

/*- Defined values for 
	attribute AGM8190_ATTR_ARBITRARY_BINARY_ALIGNMENT */

#define AGM8190_VAL_BINARY_ALIGNMENT_LEFT                   0
#define AGM8190_VAL_BINARY_ALIGNMENT_RIGHT                  1

/*- Defined values for 
	attribute AGM8190_ATTR_OUTPUT_REFERENCE_CLOCK_SOURCE
	parameter Source in function AgM8190_GetReferenceClockSourceSupported */

#define AGM8190_VAL_REFERENCE_CLOCK_SOURCE_EXTERNAL         1
#define AGM8190_VAL_REFERENCE_CLOCK_SOURCE_AXI              2
#define AGM8190_VAL_REFERENCE_CLOCK_SOURCE_INTERNAL         0

/*- Defined values for 
	attribute AGM8190_ATTR_INSTRUMENT_CHANNEL_COUPLING_ENABLED */

#define AGM8190_VAL_CHANNEL_COUPLING_STATE_ON               1
#define AGM8190_VAL_CHANNEL_COUPLING_STATE_OFF              0

/*- Defined values for 
	attribute AGM8190_ATTR_OUTPUT_ROUTE */

#define AGM8190_VAL_OUTPUT_ROUTE_DAC                        0
#define AGM8190_VAL_OUTPUT_ROUTE_AC                         1
#define AGM8190_VAL_OUTPUT_ROUTE_DC                         2

/*- Defined values for 
	attribute AGM8190_ATTR_ARBITRARY_BIT_RESOLUTION_MODE */

#define AGM8190_VAL_BIT_RESOLUTION_MODE_SPEED               0
#define AGM8190_VAL_BIT_RESOLUTION_MODE_PRECISION           1
#define AGM8190_VAL_BIT_RESOLUTION_MODE_INTERPOLATION_X3    2
#define AGM8190_VAL_BIT_RESOLUTION_MODE_INTERPOLATION_X12   3
#define AGM8190_VAL_BIT_RESOLUTION_MODE_INTERPOLATION_X24   4
#define AGM8190_VAL_BIT_RESOLUTION_MODE_INTERPOLATION_X48   5

/*- Defined values for 
	attribute AGM8190_ATTR_ARBITRARY_DAC_FORMAT
	attribute AGM8190_ATTR_ARBITRARY_DC_FORMAT
	attribute AGM8190_ATTR_ARBITRARY_AC_FORMAT
	parameter Format in function AgM8190_ArbitraryConfigureAC
	parameter Format in function AgM8190_ArbitraryConfigureDC
	parameter Format in function AgM8190_ArbitraryConfigureDAC */

#define AGM8190_VAL_FORMAT_RZ                               0
#define AGM8190_VAL_FORMAT_NRZ                              1
#define AGM8190_VAL_FORMAT_DNRZ                             2
#define AGM8190_VAL_FORMAT_DOUBLET                          3

/*- Defined values for 
	attribute AGM8190_ATTR_TRIGGER_IMPEDANCE
	attribute AGM8190_ATTR_TRIGGER_EVENT_IMPEDANCE
	parameter Impedance in function AgM8190_TriggerConfigureTrigger
	parameter Impedance in function AgM8190_TriggerConfigureEvent */

#define AGM8190_VAL_IMPEDANCE_LOW                           0
#define AGM8190_VAL_IMPEDANCE_HIGH                          1

/*- Defined values for 
	attribute AGM8190_ATTR_TRIGGER_SLOPE
	attribute AGM8190_ATTR_TRIGGER_EVENT_SLOPE
	parameter Slope in function AgM8190_TriggerConfigureTrigger
	parameter Slope in function AgM8190_TriggerConfigureEvent */

#define AGM8190_VAL_SLOPE_POSITIVE                          0
#define AGM8190_VAL_SLOPE_NEGATIVE                          1
#define AGM8190_VAL_SLOPE_EITHER                            2

/*- Defined values for */

#define AGM8190_VAL_TRIGGER_SOURCE_EXTERNAL                 1
#define AGM8190_VAL_TRIGGER_SOURCE_INTERNAL                 3

/*- Defined values for 
	attribute AGM8190_ATTR_TRIGGER_MODE
	parameter TriggerMode in function AgM8190_TriggerConfigureMode */

#define AGM8190_VAL_TRIGGER_MODE_AUTO                       0
#define AGM8190_VAL_TRIGGER_MODE_TRIGGERED                  1

/*- Defined values for 
	attribute AGM8190_ATTR_TRIGGER_ARM_MODE
	parameter ArmMode in function AgM8190_TriggerConfigureMode */

#define AGM8190_VAL_ARM_MODE_ARMED                          0
#define AGM8190_VAL_ARM_MODE_SELF                           1

/*- Defined values for 
	attribute AGM8190_ATTR_ARBITRARY_SEQUENCING_MODE */

#define AGM8190_VAL_SEQUENCING_MODE_ARBITRARY               0
#define AGM8190_VAL_SEQUENCING_MODE_ST_SEQUENCE             1
#define AGM8190_VAL_SEQUENCING_MODE_ST_SCENARIO             2

/*- Defined values for 
	attribute AGM8190_ATTR_WAVEFORM_VALID_BIT_WIDTH */

#define AGM8190_VAL_VALID_BIT_WIDTH_LOWER_BITS              0
#define AGM8190_VAL_VALID_BIT_WIDTH_ALL_BITS                1

/*- Defined values for 
	attribute AGM8190_ATTR_TRIGGER_GATE_MODE
	parameter GateMode in function AgM8190_TriggerConfigureMode */

#define AGM8190_VAL_GATE_MODE_GATED                         0
#define AGM8190_VAL_GATE_MODE_TRIGGERED                     1

/*- Defined values for 
	parameter FileType in function AgM8190_WaveformImport
	parameter FileType in function AgM8190_WaveformImportIQ
	parameter FileType in function AgM8190_ImportIQToFile */

#define AGM8190_VAL_WAVEFORM_FILE_TYPE_TXT                  0
#define AGM8190_VAL_WAVEFORM_FILE_TYPE_TXT14                2
#define AGM8190_VAL_WAVEFORM_FILE_TYPE_BIN                  3
#define AGM8190_VAL_WAVEFORM_FILE_TYPE_BIN6030              4
#define AGM8190_VAL_WAVEFORM_FILE_TYPE_IQBIN                5
#define AGM8190_VAL_WAVEFORM_FILE_TYPE_BIN5110              6
#define AGM8190_VAL_WAVEFORM_FILE_TYPE_MAT89600             7
#define AGM8190_VAL_WAVEFORM_FILE_TYPE_CSV                  8
#define AGM8190_VAL_WAVEFORM_FILE_TYPEDSA90000              9
#define AGM8190_VAL_WAVEFORM_FILE_TYPEN7617B                10
#define AGM8190_VAL_WAVEFORM_FILE_TYPE_SIG_STUDIO_ENCRYPTED 10

/*- Defined values for 
	parameter PaddingType in function AgM8190_WaveformImport
	parameter PaddingType in function AgM8190_WaveformImportIQ */

#define AGM8190_VAL_WAVEFORM_PADDING_TYPE_FILL              0
#define AGM8190_VAL_WAVEFORM_PADDING_TYPE_REPEAT_PATTERN    1

/*- Defined values for 
	attribute AGM8190_ATTR_SAMPLE_CLOCK_OUTPUT
	parameter Output in function AgM8190_SampleClockConfigure */

#define AGM8190_VAL_SAMPLE_CLOCK_OUTPUT_INTERNAL            0
#define AGM8190_VAL_SAMPLE_CLOCK_OUTPUT_EXTERNAL            1

/*- Defined values for 
	attribute AGM8190_ATTR_WAVEFORM_ADVANCEMENT_MODE
	attribute AGM8190_ATTR_SCENARIO_ADVANCEMENT_MODE
	parameter AdvancementMode in function AgM8190_SequenceGetAdvancementMode
	parameter AdvancementMode in function AgM8190_SequenceSetAdvancementMode */

#define AGM8190_VAL_ADVANCEMENT_MODE_AUTO                   0
#define AGM8190_VAL_ADVANCEMENT_MODE_CONDITIONAL            1
#define AGM8190_VAL_ADVANCEMENT_MODE_REPEAT                 2
#define AGM8190_VAL_ADVANCEMENT_MODE_SINGLE                 3

/*- Defined values for 
	parameter MarkerType in function AgM8190_MarkerConfigure */

#define AGM8190_VAL_MARKER_TYPE_SAMPLE                      0
#define AGM8190_VAL_MARKER_TYPE_SYNC                        1

/*- Defined values for 
	attribute AGM8190_ATTR_TRIGGER_ENABLE_EVENT_SOURCE
	attribute AGM8190_ATTR_TRIGGER_ADVANCEMENT_EVENT_SOURCE */

#define AGM8190_VAL_TRIGGER_EVENT_SOURCE_TRIGGER            0
#define AGM8190_VAL_TRIGGER_EVENT_SOURCE_EVENT              1

/*- Defined values for 
	parameter Register in function AgM8190_StatusGetRegister
	parameter Register in function AgM8190_StatusSetRegister */

#define AGM8190_VAL_STATUS_REGISTER_STATUS_BYTE             0
#define AGM8190_VAL_STATUS_REGISTER_STANDARD_EVENT          1
#define AGM8190_VAL_STATUS_REGISTER_OPERATION               2
#define AGM8190_VAL_STATUS_REGISTER_OPERATION_RUN           3
#define AGM8190_VAL_STATUS_REGISTER_QUESTIONABLE            4
#define AGM8190_VAL_STATUS_REGISTER_QUESTIONABLE_VOLTAGE    5
#define AGM8190_VAL_STATUS_REGISTER_QUESTIONABLE_FREQUENCY  6
#define AGM8190_VAL_STATUS_REGISTER_QUESTIONABLE_SEQUENCE   7

/*- Defined values for 
	parameter SubRegister in function AgM8190_StatusGetRegister
	parameter SubRegister in function AgM8190_StatusSetRegister */

#define AGM8190_VAL_STATUS_SUB_REGISTER_CONDITION           0
#define AGM8190_VAL_STATUS_SUB_REGISTER_NEGATIVE_TRANSITION 1
#define AGM8190_VAL_STATUS_SUB_REGISTER_POSITIVE_TRANSITION 2
#define AGM8190_VAL_STATUS_SUB_REGISTER_EVENT               3
#define AGM8190_VAL_STATUS_SUB_REGISTER_ENABLE              4

/*- Defined values for 
	parameter Reason in function AgM8190_StatusConfigureServiceRequest */

#define AGM8190_VAL_STATUSSRQ_REASON_STB_MAV                                       1
#define AGM8190_VAL_STATUSSRQ_REASON_STB_ERROR_QUEUE                               2
#define AGM8190_VAL_STATUSSRQ_REASON_ESR_OPC                                       4
#define AGM8190_VAL_STATUSSRQ_REASON_ESR_QUERY_ERROR                               8
#define AGM8190_VAL_STATUSSRQ_REASON_ESR_DEVICE_ERROR                              16
#define AGM8190_VAL_STATUSSRQ_REASON_ESR_EXECUTION_ERROR                           32
#define AGM8190_VAL_STATUSSRQ_REASON_ESR_COMMAND_ERROR                             64
#define AGM8190_VAL_STATUSSRQ_REASON_ESR_POWER_ON                                  128
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_VOLTAGE_CHANNEL1                         256
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_VOLTAGE_CHANNEL2                         512
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_FREQUENCY_CHANNEL1                       1024
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_FREQUENCY_CHANNEL2                       2048
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_SEQUENCE_DATA_ERROR_CHANNEL1             4096
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_SEQUENCE_DATA_ERROR_CHANNEL2             8192
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_SEQUENCE_LINEAR_PLAY_TIME_ERROR_CHANNEL1 16384
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_SEQUENCE_LINEAR_PLAY_TIME_ERROR_CHANNEL2 32768
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_SEQUENCE_STREAMING_DATA_ERROR_CHANNEL1   65536
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_SEQUENCE_STREAMING_DATA_ERROR_CHANNEL2   131072
#define AGM8190_VAL_STATUSSRQ_REASON_OPER_RUN_CHANNEL1                             262144
#define AGM8190_VAL_STATUSSRQ_REASON_OPER_RUN_CHANNEL2                             524288
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_AMPLITUDE_CLIPPED_CHANNEL1               1048576
#define AGM8190_VAL_STATUSSRQ_REASON_QUES_AMPLITUDE_CLIPPED_CHANNEL2               2097152

/*- Defined values for 
	parameter DataType in function AgM8190_WaveformImportIQ */

#define AGM8190_VAL_WAVEFORM_DATA_TYPE_IONLY                0
#define AGM8190_VAL_WAVEFORM_DATA_TYPE_QONLY                1
#define AGM8190_VAL_WAVEFORM_DATA_TYPE_BOTH                 2

/*- Defined values for 
	parameter Action in function AgM8190_ActionSequenceAppend */

#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_CARRIER_FREQUENCY 0
#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_PHASE_OFFSET      1
#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_PHASE_RESET       2
#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_PHASE_BUMP        3
#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_SWEEP_RATE        4
#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_SWEEP_RUN         5
#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_SWEEP_HOLD        6
#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_SWEEP_RESTART     7
#define AGM8190_VAL_ACTION_SEQUENCE_ACTION_TYPE_AMPLITUDE         8

/*- Defined values for 
	attribute AGM8190_ATTR_MULTI_MODULE_MODE */

#define AGM8190_VAL_MULTI_MODULE_MODENOR_MAL                0
#define AGM8190_VAL_MULTI_MODULE_MODEMAS_TER                1
#define AGM8190_VAL_MULTI_MODULE_MODESLA_VE                 2

/*- Defined values for 
	attribute AGM8190_ATTR_ADVANCEMENT_EVENT_SOURCE_EX */

#define AGM8190_VAL_EVENT_SOURCE_TRIGGER                    0
#define AGM8190_VAL_EVENT_SOURCE_EVENT                      1
#define AGM8190_VAL_EVENT_SOURCE_INTERNAL                   2


/**************************************************************************** 
 *---------------- Instrument Driver Function Declarations -----------------* 
 ****************************************************************************/

/*- AgM8190 */

ViStatus _VI_FUNC AgM8190_init ( ViRsrc ResourceName, ViBoolean IdQuery, ViBoolean Reset, ViSession* Vi );
ViStatus _VI_FUNC AgM8190_close ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_InitWithOptions ( ViRsrc ResourceName, ViBoolean IdQuery, ViBoolean Reset, ViConstString OptionsString, ViSession* Vi );

/*- Utility */

ViStatus _VI_FUNC AgM8190_revision_query ( ViSession Vi, ViChar DriverRev[], ViChar InstrRev[] );
ViStatus _VI_FUNC AgM8190_error_message ( ViSession Vi, ViStatus ErrorCode, ViChar ErrorMessage[] );
ViStatus _VI_FUNC AgM8190_GetError ( ViSession Vi, ViStatus* ErrorCode, ViInt32 ErrorDescriptionBufferSize, ViChar ErrorDescription[] );
ViStatus _VI_FUNC AgM8190_ClearError ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_ClearInterchangeWarnings ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_GetNextCoercionRecord ( ViSession Vi, ViInt32 CoercionRecordBufferSize, ViChar CoercionRecord[] );
ViStatus _VI_FUNC AgM8190_GetNextInterchangeWarning ( ViSession Vi, ViInt32 InterchangeWarningBufferSize, ViChar InterchangeWarning[] );
ViStatus _VI_FUNC AgM8190_InvalidateAllAttributes ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_ResetInterchangeCheck ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_Disable ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_error_query ( ViSession Vi, ViInt32* ErrorCode, ViChar ErrorMessage[] );
ViStatus _VI_FUNC AgM8190_LockSession ( ViSession Vi, ViBoolean* CallerHasLock );
ViStatus _VI_FUNC AgM8190_reset ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_ResetWithDefaults ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_self_test ( ViSession Vi, ViInt16* TestResult, ViChar TestMessage[] );
ViStatus _VI_FUNC AgM8190_UnlockSession ( ViSession Vi, ViBoolean* CallerHasLock );
ViStatus _VI_FUNC AgM8190_GetChannelName ( ViSession Vi, ViInt32 Index, ViInt32 NameBufferSize, ViChar Name[] );

/*- Attribute Accessors */

ViStatus _VI_FUNC AgM8190_GetAttributeViInt32 ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViInt32* AttributeValue );
ViStatus _VI_FUNC AgM8190_GetAttributeViReal64 ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViReal64* AttributeValue );
ViStatus _VI_FUNC AgM8190_GetAttributeViBoolean ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViBoolean* AttributeValue );
ViStatus _VI_FUNC AgM8190_GetAttributeViSession ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViSession* AttributeValue );
ViStatus _VI_FUNC AgM8190_GetAttributeViString ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViInt32 AttributeValueBufferSize, ViChar AttributeValue[] );
ViStatus _VI_FUNC AgM8190_SetAttributeViInt32 ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViInt32 AttributeValue );
ViStatus _VI_FUNC AgM8190_SetAttributeViReal64 ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViReal64 AttributeValue );
ViStatus _VI_FUNC AgM8190_SetAttributeViBoolean ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViBoolean AttributeValue );
ViStatus _VI_FUNC AgM8190_SetAttributeViSession ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViSession AttributeValue );
ViStatus _VI_FUNC AgM8190_SetAttributeViString ( ViSession Vi, ViConstString RepCapIdentifier, ViAttr AttributeID, ViConstString AttributeValue );
ViStatus _VI_FUNC AgM8190_GetAttributeViInt64 ( ViSession Vi, ViConstString RepCapIdentifier, ViInt32 AttributeID, ViInt64* AttributeValue );
ViStatus _VI_FUNC AgM8190_SetAttributeViInt64 ( ViSession Vi, ViConstString RepCapIdentifier, ViInt32 AttributeID, ViInt64 AttributeValue );

/*- General */

ViStatus _VI_FUNC AgM8190_ConfigureOutputEnabled ( ViSession Vi, ViConstString ChannelName, ViBoolean Enabled );
ViStatus _VI_FUNC AgM8190_ConfigureOutputMode ( ViSession Vi, ViInt32 OutputMode );
ViStatus _VI_FUNC AgM8190_ConfigureRefClockSource ( ViSession Vi, ViInt32 Source );

/*- Arbitrary Waveform */

ViStatus _VI_FUNC AgM8190_ConfigureSampleRate ( ViSession Vi, ViReal64 SampleRate );
ViStatus _VI_FUNC AgM8190_QueryArbWfmCapabilities ( ViSession Vi, ViInt32* MaxNumWfms, ViInt32* WfmQuantum, ViInt32* MinWfmSize, ViInt32* MaxWfmSize );
ViStatus _VI_FUNC AgM8190_ClearArbWaveform ( ViSession Vi, ViInt32 Handle );
ViStatus _VI_FUNC AgM8190_ConfigureArbWaveform ( ViSession Vi, ViConstString ChannelName, ViInt32 Handle, ViReal64 Gain, ViReal64 Offset );
ViStatus _VI_FUNC AgM8190_CreateArbWaveform ( ViSession Vi, ViInt32 Size, ViReal64 Data[], ViInt32* Handle );

/*- Arbitrary Sequence */

ViStatus _VI_FUNC AgM8190_QueryArbSeqCapabilities ( ViSession Vi, ViInt32* MaxNumSeqs, ViInt32* MinSeqLength, ViInt32* MaxSeqLength, ViInt32* MaxLoopCount );
ViStatus _VI_FUNC AgM8190_ClearArbMemory ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_ClearArbSequence ( ViSession Vi, ViInt32 Handle );
ViStatus _VI_FUNC AgM8190_ConfigureArbSequence ( ViSession Vi, ViConstString ChannelName, ViInt32 Handle, ViReal64 Gain, ViReal64 Offset );
ViStatus _VI_FUNC AgM8190_CreateArbSequence ( ViSession Vi, ViInt32 Length, ViInt32 WfmHandle[], ViInt32 LoopCount[], ViInt32* Handle );

/*- Trigger */

ViStatus _VI_FUNC AgM8190_ConfigureTriggerSource ( ViSession Vi, ViConstString ChannelName, ViInt32 Source );

/*- Internal Trigger */

ViStatus _VI_FUNC AgM8190_ConfigureInternalTriggerRate ( ViSession Vi, ViReal64 Rate );

/*- Action */

ViStatus _VI_FUNC AgM8190_AbortGeneration ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_InitiateGeneration ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_SendSoftwareTrigger ( ViSession Vi );

/*- Instrument Specific */

ViStatus _VI_FUNC AgM8190_ChannelInitiateGeneration ( ViSession Vi, ViConstString Channel );
ViStatus _VI_FUNC AgM8190_ChannelAbortGeneration ( ViSession Vi, ViConstString Channel );

/*- Output */

ViStatus _VI_FUNC AgM8190_OutputConfigureDelay ( ViSession Vi, ViConstString Channel, ViReal64 CoarseDelay, ViReal64 FineDelay, ViReal64 DifferentialOffset );
ViStatus _VI_FUNC AgM8190_GetReferenceClockSourceSupported ( ViSession Vi, ViInt32 Source, ViBoolean* ReferenceClockSourceSupported );

/*- SampleClock */

ViStatus _VI_FUNC AgM8190_SampleClockGetSampleClockSource ( ViSession Vi, ViConstString Channel, ViInt32* SampleClockSource );
ViStatus _VI_FUNC AgM8190_SampleClockSetSampleClockSource ( ViSession Vi, ViConstString Channel, ViInt32 SampleClockSource );
ViStatus _VI_FUNC AgM8190_SampleClockConfigure ( ViSession Vi, ViConstString Channel, ViInt32 Source, ViInt32 Output );

/*- Arbitrary */

ViStatus _VI_FUNC AgM8190_ArbitraryClearMemory ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_ArbitraryConfigureAC ( ViSession Vi, ViConstString Channel, ViReal64 Amplitude, ViInt32 Format );
ViStatus _VI_FUNC AgM8190_ArbitraryConfigureDC ( ViSession Vi, ViConstString Channel, ViReal64 Amplitude, ViInt32 Format, ViReal64 Offset );
ViStatus _VI_FUNC AgM8190_ArbitraryConfigureDAC ( ViSession Vi, ViConstString Channel, ViReal64 Amplitude, ViInt32 Format, ViReal64 Offset );

/*- Waveform */

ViStatus _VI_FUNC AgM8190_WaveformCreateChannelWaveform ( ViSession Vi, ViConstString Channel, ViInt32 DataBufferSize, ViReal64 Data[], ViInt32* Val );
ViStatus _VI_FUNC AgM8190_WaveformConfigure ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViReal64 Amplitude, ViReal64 Offset );
ViStatus _VI_FUNC AgM8190_WaveformCreateChannelWaveformInt16 ( ViSession Vi, ViConstString Channel, ViInt32 DataBufferSize, ViInt16 Data[], ViInt32* Val );
ViStatus _VI_FUNC AgM8190_WaveformCreateChannelWaveformChunkInt16 ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 Position, ViInt32 Length, ViInt32 DataBufferSize, ViInt16 Data[], ViInt32* Val );
ViStatus _VI_FUNC AgM8190_WaveformCreateChannelWaveformChunkInt16WithInit ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 Position, ViInt32 Length, ViInt32 DataBufferSize, ViInt16 Data[], ViInt16 Init, ViInt32* Val );
ViStatus _VI_FUNC AgM8190_WaveformCreateChannelWaveformInt16WriteOnly ( ViSession Vi, ViConstString Channel, ViInt32 DataBufferSize, ViInt16 Data[], ViInt32* Val );
ViStatus _VI_FUNC AgM8190_WaveformClear ( ViSession Vi, ViConstString Channel, ViInt32 Handle );
ViStatus _VI_FUNC AgM8190_WaveformClearAll ( ViSession Vi, ViConstString Channel );
ViStatus _VI_FUNC AgM8190_WaveformQueryFreeMemory ( ViSession Vi, ViConstString Channel, ViInt64* BytesAvailable, ViInt64* BytesUsed, ViInt64* ContiguousBytesAvailable );
ViStatus _VI_FUNC AgM8190_WaveformGetComment ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 CommentBufferSize, ViChar Comment[] );
ViStatus _VI_FUNC AgM8190_WaveformSetComment ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViConstString Comment );
ViStatus _VI_FUNC AgM8190_WaveformGetName ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 NameBufferSize, ViChar Name[] );
ViStatus _VI_FUNC AgM8190_WaveformSetName ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViConstString Name );
ViStatus _VI_FUNC AgM8190_WaveformImport ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViConstString FileName, ViInt32 FileType, ViInt32 PaddingType );
ViStatus _VI_FUNC AgM8190_WaveformImportIQ ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViConstString FileName, ViInt32 FileType, ViInt32 DataType, ViBoolean MarkerFlagEnabled, ViInt32 PaddingType );
ViStatus _VI_FUNC AgM8190_CreateChannelIQWaveformWithInit ( ViSession Vi, ViConstString Channel, ViInt32 Length, ViInt16 IValue, ViInt16 QValue, ViInt32* Val );
ViStatus _VI_FUNC AgM8190_ImportIQToFile ( ViSession Vi, ViConstString FileName, ViInt32 FileType, ViBoolean MarkerFlagEnabled );

/*- Sequence */

ViStatus _VI_FUNC AgM8190_SequenceCreate ( ViSession Vi, ViConstString Channel, ViInt32 WfmHandleBufferSize, ViInt32 WfmHandle[], ViInt32 LoopCountBufferSize, ViInt32 LoopCount[], ViInt32* Val );
ViStatus _VI_FUNC AgM8190_SequenceConfigure ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViReal64 Amplitude, ViReal64 Offset );
ViStatus _VI_FUNC AgM8190_SequenceSetData ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 Step, ViInt32 DataBufferSize, ViInt32 Data[] );
ViStatus _VI_FUNC AgM8190_SequenceGetData ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 Step, ViInt32 Length, ViInt32 DataBufferSize, ViInt32 Data[], ViInt32* DataActualSize );
ViStatus _VI_FUNC AgM8190_SequenceClear ( ViSession Vi, ViConstString Channel, ViInt32 Handle );
ViStatus _VI_FUNC AgM8190_SequenceClearAll ( ViSession Vi, ViConstString Channel );
ViStatus _VI_FUNC AgM8190_SequenceGetLoopCount ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt64* LoopCount );
ViStatus _VI_FUNC AgM8190_SequenceSetLoopCount ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt64 LoopCount );
ViStatus _VI_FUNC AgM8190_SequenceGetComment ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 CommentBufferSize, ViChar Comment[] );
ViStatus _VI_FUNC AgM8190_SequenceSetComment ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViConstString Comment );
ViStatus _VI_FUNC AgM8190_SequenceGetAdvancementMode ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32* AdvancementMode );
ViStatus _VI_FUNC AgM8190_SequenceSetAdvancementMode ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 AdvancementMode );
ViStatus _VI_FUNC AgM8190_SequenceGetName ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViInt32 NameBufferSize, ViChar Name[] );
ViStatus _VI_FUNC AgM8190_SequenceSetName ( ViSession Vi, ViConstString Channel, ViInt32 Handle, ViConstString Name );
ViStatus _VI_FUNC AgM8190_SequenceQueryFreeMemory ( ViSession Vi, ViConstString Channel, ViInt32* Available, ViInt32* Used, ViInt32* ContiguousAvailable );

/*- SequenceTable */

ViStatus _VI_FUNC AgM8190_SequenceTableReset ( ViSession Vi, ViConstString Channel );
ViStatus _VI_FUNC AgM8190_SequenceTableSetData ( ViSession Vi, ViConstString Channel, ViInt32 TableIndex, ViInt32 DataBufferSize, ViInt32 Data[] );
ViStatus _VI_FUNC AgM8190_SequenceTableGetData ( ViSession Vi, ViConstString Channel, ViInt32 TableIndex, ViInt32 Length, ViInt32 DataBufferSize, ViInt32 Data[], ViInt32* DataActualSize );

/*- DigitalUpConversion */

ViStatus _VI_FUNC AgM8190_DigitalUpConversionSetCarrierFrequency ( ViSession Vi, ViConstString Channel, ViReal64 FrequencyIntegral, ViReal64 FrequencyFractional );
ViStatus _VI_FUNC AgM8190_DigitalUpConversionGetCarrierFrequency ( ViSession Vi, ViConstString Channel, ViReal64* FrequencyIntegral, ViReal64* FrequencyFractional );
ViStatus _VI_FUNC AgM8190_DigitalUpConversionGetCarrierFrequencyMin ( ViSession Vi, ViConstString Channel, ViReal64* FrequencyIntegral, ViReal64* FrequencyFractional );
ViStatus _VI_FUNC AgM8190_DigitalUpConversionGetCarrierFrequencyMax ( ViSession Vi, ViConstString Channel, ViReal64* FrequencyIntegral, ViReal64* FrequencyFractional );

/*- ActionSequence */

ViStatus _VI_FUNC AgM8190_ActionSequenceCreate ( ViSession Vi, ViConstString Channel, ViInt32* Val );
ViStatus _VI_FUNC AgM8190_ActionSequenceAppend ( ViSession Vi, ViConstString Channel, ViInt32 SequenceID, ViInt32 Action, ViReal64 Value1, ViReal64 Value2 );
ViStatus _VI_FUNC AgM8190_ActionSequenceDelete ( ViSession Vi, ViConstString Channel, ViInt32 SequenceID );
ViStatus _VI_FUNC AgM8190_ActionSequenceDeleteAll ( ViSession Vi, ViConstString Channel );

/*- AmplitudeTable */

ViStatus _VI_FUNC AgM8190_AmplitudeTableSetData ( ViSession Vi, ViConstString Channel, ViInt32 TableIndex, ViInt32 DataBufferSize, ViReal64 Data[] );
ViStatus _VI_FUNC AgM8190_AmplitudeTableGetData ( ViSession Vi, ViConstString Channel, ViInt32 TableIndex, ViInt32 Length, ViInt32 DataBufferSize, ViReal64 Data[], ViInt32* DataActualSize );
ViStatus _VI_FUNC AgM8190_AmplitudeTableReset ( ViSession Vi, ViConstString Channel );

/*- FrequencyTable */

ViStatus _VI_FUNC AgM8190_FrequencyTableSetData ( ViSession Vi, ViConstString Channel, ViReal64 TableIndex, ViInt32 DataBufferSize, ViReal64 Data[] );
ViStatus _VI_FUNC AgM8190_FrequencyTableGetData ( ViSession Vi, ViConstString Channel, ViReal64 TableIndex, ViInt32 Length, ViInt32 DataBufferSize, ViReal64 Data[], ViInt32* DataActualSize );
ViStatus _VI_FUNC AgM8190_FrequencyTableReset ( ViSession Vi, ViConstString Channel );

/*- System */

ViStatus _VI_FUNC AgM8190_SystemLoadConfiguration ( ViSession Vi, ViConstString FileName );
ViStatus _VI_FUNC AgM8190_SystemStoreConfiguration ( ViSession Vi, ViConstString FileName );
ViStatus _VI_FUNC AgM8190_SystemWaitForOperationComplete ( ViSession Vi, ViInt32 MaxTimeMilliseconds );
ViStatus _VI_FUNC AgM8190_SystemIoRead ( ViSession Vi, ViInt32 Size, ViChar Value[], ViInt32* ActualSize );
ViStatus _VI_FUNC AgM8190_SystemIoWrite ( ViSession Vi, ViConstString Value );
ViStatus _VI_FUNC AgM8190_SystemPowerOnSelfTest ( ViSession Vi, ViInt32 TestMessageBufferSize, ViChar TestMessage[] );

/*- Marker */

ViStatus _VI_FUNC AgM8190_MarkerConfigure ( ViSession Vi, ViConstString Channel, ViInt32 MarkerType, ViReal64 Amplitude, ViReal64 Offset );

/*- Trigger */

ViStatus _VI_FUNC AgM8190_TriggerSendSoftwareTrigger ( ViSession Vi, ViConstString Channel );
ViStatus _VI_FUNC AgM8190_TriggerSendSoftwareEvent ( ViSession Vi, ViConstString Channel );
ViStatus _VI_FUNC AgM8190_TriggerSendSoftwareEnable ( ViSession Vi, ViConstString Channel );
ViStatus _VI_FUNC AgM8190_TriggerConfigureTrigger ( ViSession Vi, ViInt32 Impedance, ViInt32 Slope, ViReal64 Threshold );
ViStatus _VI_FUNC AgM8190_TriggerConfigureEvent ( ViSession Vi, ViInt32 Impedance, ViInt32 Slope, ViReal64 Threshold );
ViStatus _VI_FUNC AgM8190_TriggerConfigureMode ( ViSession Vi, ViConstString Channel, ViInt32 ArmMode, ViInt32 GateMode, ViInt32 TriggerMode );

/*- Status */

ViStatus _VI_FUNC AgM8190_StatusGetFrequencyStable ( ViSession Vi, ViConstString Channel, ViBoolean* FrequencyStableState );
ViStatus _VI_FUNC AgM8190_StatusGetGenerating ( ViSession Vi, ViConstString Channel, ViBoolean* Generating );
ViStatus _VI_FUNC AgM8190_StatusGetOutputVoltageOK ( ViSession Vi, ViConstString Channel, ViBoolean* OutputProtectionState );
ViStatus _VI_FUNC AgM8190_StatusClear ( ViSession Vi );
ViStatus _VI_FUNC AgM8190_StatusConfigureServiceRequest ( ViSession Vi, ViInt32 Reason );
ViStatus _VI_FUNC AgM8190_StatusGetRegister ( ViSession Vi, ViInt32 Register, ViInt32 SubRegister, ViInt32* RetVal );
ViStatus _VI_FUNC AgM8190_StatusSetRegister ( ViSession Vi, ViInt32 Register, ViInt32 SubRegister, ViInt32 Val );
ViStatus _VI_FUNC AgM8190_GetStatusAmplitudeClipped ( ViSession Vi, ViConstString Channel, ViBoolean* AmplitudeClipped );

/*- Memory */

ViStatus _VI_FUNC AgM8190_MemoryCopy ( ViSession Vi, ViInt32 SourceBufferSize, ViConstString Source, ViInt32 DestinationBufferSize, ViConstString Destination );
ViStatus _VI_FUNC AgM8190_MemoryDelete ( ViSession Vi, ViConstString FileName, ViConstString DirectoryName );
ViStatus _VI_FUNC AgM8190_MemoryStoreData ( ViSession Vi, ViConstString FileName, ViInt32 DataBufferSize, ViChar Data[] );
ViStatus _VI_FUNC AgM8190_MemoryLoadData ( ViSession Vi, ViConstString FileName, ViInt32 DataBufferSize, ViChar Data[], ViInt32* DataActualSize );
ViStatus _VI_FUNC AgM8190_MemoryCreateFolder ( ViSession Vi, ViConstString DirectoryName );
ViStatus _VI_FUNC AgM8190_MemoryMove ( ViSession Vi, ViInt32 SourceBufferSize, ViConstString Source, ViInt32 DestinationBufferSize, ViConstString Destination );
ViStatus _VI_FUNC AgM8190_MemoryDeleteFolder ( ViSession Vi, ViConstString DirectoryName );
ViStatus _VI_FUNC AgM8190_MemoryQueryCatalog ( ViSession Vi, ViInt64* UsedMemory, ViInt64* AvailableMemory, ViInt32 FileEntriesBufferSize, ViChar FileEntries[] );


/**************************************************************************** 
 *----------------- Instrument Error And Completion Codes ------------------* 
 ****************************************************************************/
#ifndef _IVIC_ERROR_BASE_DEFINES_
#define _IVIC_ERROR_BASE_DEFINES_

#define IVIC_WARN_BASE                           (0x3FFA0000L)
#define IVIC_CROSS_CLASS_WARN_BASE               (IVIC_WARN_BASE + 0x1000)
#define IVIC_CLASS_WARN_BASE                     (IVIC_WARN_BASE + 0x2000)
#define IVIC_SPECIFIC_WARN_BASE                  (IVIC_WARN_BASE + 0x4000)

#define IVIC_ERROR_BASE                          (0xBFFA0000L)
#define IVIC_CROSS_CLASS_ERROR_BASE              (IVIC_ERROR_BASE + 0x1000)
#define IVIC_CLASS_ERROR_BASE                    (IVIC_ERROR_BASE + 0x2000)
#define IVIC_SPECIFIC_ERROR_BASE                 (IVIC_ERROR_BASE + 0x4000)
#define IVIC_LXISYNC_ERROR_BASE                  (IVIC_ERROR_BASE + 0x2000)

#endif


#define AGM8190_ERROR_CANNOT_RECOVER                        (IVIC_ERROR_BASE + 0x0000)
#define AGM8190_ERROR_INSTRUMENT_STATUS                     (IVIC_ERROR_BASE + 0x0001)
#define AGM8190_ERROR_CANNOT_OPEN_FILE                      (IVIC_ERROR_BASE + 0x0002)
#define AGM8190_ERROR_READING_FILE                          (IVIC_ERROR_BASE + 0x0003)
#define AGM8190_ERROR_WRITING_FILE                          (IVIC_ERROR_BASE + 0x0004)
#define AGM8190_ERROR_INVALID_PATHNAME                      (IVIC_ERROR_BASE + 0x000B)
#define AGM8190_ERROR_INVALID_VALUE                         (IVIC_ERROR_BASE + 0x0010)
#define AGM8190_ERROR_FUNCTION_NOT_SUPPORTED                (IVIC_ERROR_BASE + 0x0011)
#define AGM8190_ERROR_ATTRIBUTE_NOT_SUPPORTED               (IVIC_ERROR_BASE + 0x0012)
#define AGM8190_ERROR_VALUE_NOT_SUPPORTED                   (IVIC_ERROR_BASE + 0x0013)
#define AGM8190_ERROR_NOT_INITIALIZED                       (IVIC_ERROR_BASE + 0x001D)
#define AGM8190_ERROR_UNKNOWN_CHANNEL_NAME                  (IVIC_ERROR_BASE + 0x0020)
#define AGM8190_ERROR_TOO_MANY_OPEN_FILES                   (IVIC_ERROR_BASE + 0x0023)
#define AGM8190_ERROR_CHANNEL_NAME_REQUIRED                 (IVIC_ERROR_BASE + 0x0044)
#define AGM8190_ERROR_MISSING_OPTION_NAME                   (IVIC_ERROR_BASE + 0x0049)
#define AGM8190_ERROR_MISSING_OPTION_VALUE                  (IVIC_ERROR_BASE + 0x004A)
#define AGM8190_ERROR_BAD_OPTION_NAME                       (IVIC_ERROR_BASE + 0x004B)
#define AGM8190_ERROR_BAD_OPTION_VALUE                      (IVIC_ERROR_BASE + 0x004C)
#define AGM8190_ERROR_OUT_OF_MEMORY                         (IVIC_ERROR_BASE + 0x0056)
#define AGM8190_ERROR_OPERATION_PENDING                     (IVIC_ERROR_BASE + 0x0057)
#define AGM8190_ERROR_NULL_POINTER                          (IVIC_ERROR_BASE + 0x0058)
#define AGM8190_ERROR_UNEXPECTED_RESPONSE                   (IVIC_ERROR_BASE + 0x0059)
#define AGM8190_ERROR_FILE_NOT_FOUND                        (IVIC_ERROR_BASE + 0x005B)
#define AGM8190_ERROR_INVALID_FILE_FORMAT                   (IVIC_ERROR_BASE + 0x005C)
#define AGM8190_ERROR_STATUS_NOT_AVAILABLE                  (IVIC_ERROR_BASE + 0x005D)
#define AGM8190_ERROR_ID_QUERY_FAILED                       (IVIC_ERROR_BASE + 0x005E)
#define AGM8190_ERROR_RESET_FAILED                          (IVIC_ERROR_BASE + 0x005F)
#define AGM8190_ERROR_RESOURCE_UNKNOWN                      (IVIC_ERROR_BASE + 0x0060)
#define AGM8190_ERROR_ALREADY_INITIALIZED                   (IVIC_ERROR_BASE + 0x0061)
#define AGM8190_ERROR_CANNOT_CHANGE_SIMULATION_STATE        (IVIC_ERROR_BASE + 0x0062)
#define AGM8190_ERROR_INVALID_NUMBER_OF_LEVELS_IN_SELECTOR  (IVIC_ERROR_BASE + 0x0063)
#define AGM8190_ERROR_INVALID_RANGE_IN_SELECTOR             (IVIC_ERROR_BASE + 0x0064)
#define AGM8190_ERROR_UNKOWN_NAME_IN_SELECTOR               (IVIC_ERROR_BASE + 0x0065)
#define AGM8190_ERROR_BADLY_FORMED_SELECTOR                 (IVIC_ERROR_BASE + 0x0066)
#define AGM8190_ERROR_UNKNOWN_PHYSICAL_IDENTIFIER           (IVIC_ERROR_BASE + 0x0067)
#define AGM8190_ERROR_INVALID_ATTRIBUTE                     (IVIC_ERROR_BASE + 0x000C)
#define AGM8190_ERROR_TYPES_DO_NOT_MATCH                    (IVIC_ERROR_BASE + 0x0015)
#define AGM8190_ERROR_IVI_ATTR_NOT_WRITABLE                 (IVIC_ERROR_BASE + 0x000D)
#define AGM8190_ERROR_IVI_ATTR_NOT_READABLE                 (IVIC_ERROR_BASE + 0x000E)
#define AGM8190_ERROR_INVALID_SESSION_HANDLE                (IVIC_ERROR_BASE + 0x1190)



#define AGM8190_SUCCESS                                     0
#define AGM8190_WARN_NSUP_ID_QUERY                          (IVIC_WARN_BASE + 0x0065)
#define AGM8190_WARN_NSUP_RESET                             (IVIC_WARN_BASE + 0x0066)
#define AGM8190_WARN_NSUP_SELF_TEST                         (IVIC_WARN_BASE + 0x0067)
#define AGM8190_WARN_NSUP_ERROR_QUERY                       (IVIC_WARN_BASE + 0x0068)
#define AGM8190_WARN_NSUP_REV_QUERY                         (IVIC_WARN_BASE + 0x0069)



#define AGM8190_ERROR_IO_GENERAL                            (IVIC_SPECIFIC_ERROR_BASE + 0x0214)
#define AGM8190_ERROR_IO_TIMEOUT                            (IVIC_SPECIFIC_ERROR_BASE + 0x0215)
#define AGM8190_ERROR_MODEL_NOT_SUPPORTED                   (IVIC_SPECIFIC_ERROR_BASE + 0x0216)
#define AGM8190_ERROR_PERSONALITY_NOT_ACTIVE                (IVIC_SPECIFIC_ERROR_BASE + 0x0211)
#define AGM8190_ERROR_PERSONALITY_NOT_LICENSED              (IVIC_SPECIFIC_ERROR_BASE + 0x0213)
#define AGM8190_ERROR_PERSONALITY_NOT_INSTALLED             (IVIC_SPECIFIC_ERROR_BASE + 0x0212)
#define AGM8190_ERROR_TRIGGER_NOT_SOFTWARE                  (IVIC_CROSS_CLASS_ERROR_BASE + 0x0001)
#define AGM8190_ERROR_NO_WFMS_AVAILABLE                     (IVIC_CLASS_ERROR_BASE + 0x0004)
#define AGM8190_ERROR_WFM_IN_USE                            (IVIC_CLASS_ERROR_BASE + 0x0008)
#define AGM8190_ERROR_NO_SEQS_AVAILABLE                     (IVIC_CLASS_ERROR_BASE + 0x0009)
#define AGM8190_ERROR_SEQ_IN_USE                            (IVIC_CLASS_ERROR_BASE + 0x000D)
#define AGM8190_ERROR_OPTION_NOT_INSTALLED                  (IVIC_SPECIFIC_ERROR_BASE + 0x0217)
#define AGM8190_ERROR_INITIALIZATION_FAILED                 (IVIC_SPECIFIC_ERROR_BASE + 0x0218)
#define AGM8190_ERROR_INVALID_SIZE                          (IVIC_SPECIFIC_ERROR_BASE + 0x0001)




/**************************************************************************** 
 *---------------------------- End Include File ----------------------------* 
 ****************************************************************************/
#if defined(__cplusplus) || defined(__cplusplus__)
}
#endif
#endif // __AGM8190_HEADER
