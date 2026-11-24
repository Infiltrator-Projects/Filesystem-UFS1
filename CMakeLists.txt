cmake_minimum_required(VERSION 3.20)
file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" UFS1_RELEASE_VERSION LIMIT_COUNT 1)
project(FilesystemUFS1 VERSION ${UFS1_RELEASE_VERSION} LANGUAGES C)
include(CTest)
include(FetchContent)
find_package(OpenSSL REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(INFILTRATR_COMMON_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(INFILTRATR_COMMON_BUILD_SHARED OFF CACHE BOOL "" FORCE)
FetchContent_Declare(infiltratr_common
 GIT_REPOSITORY https://github.com/Infiltrator-Projects/Libraries.git
 GIT_TAG d23a52693fd3212368d327e1c1302e07ae9510ec)
FetchContent_MakeAvailable(infiltratr_common)
# Common is linked into the filesystem; its development files are not installed.
set_property(DIRECTORY "${infiltratr_common_SOURCE_DIR}" PROPERTY EXCLUDE_FROM_ALL TRUE)
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/version.h" "#define LD_VERSION \"${PROJECT_VERSION}\"\n")
# Production is V2-only. Historical source worker/fixture/Kconfig remains
# in the repository for provenance and independent future qualification.
add_library(ufs1-driver SHARED
 native/ufs_native.c
 module/ufs_module.c)
set_target_properties(ufs1-driver PROPERTIES PREFIX "" OUTPUT_NAME "UFS1" SUFFIX ".so")
target_compile_definitions(ufs1-driver PRIVATE
 _GNU_SOURCE _FILE_OFFSET_BITS=64 IFS_UFS_MAJOR=1 IFS_UFS_V2_PRODUCTION=1)
target_compile_options(ufs1-driver PRIVATE
 -Wall -Wextra -Wpedantic -Werror -ffunction-sections -fdata-sections -fvisibility=hidden)
target_link_options(ufs1-driver PRIVATE
 -Wl,-z,defs -Wl,--gc-sections
 "-Wl,--version-script=${CMAKE_CURRENT_SOURCE_DIR}/module/v2-only.map")
target_include_directories(ufs1-driver PRIVATE
 "${CMAKE_CURRENT_SOURCE_DIR}/native" "${CMAKE_CURRENT_SOURCE_DIR}/compat"
 "${CMAKE_CURRENT_SOURCE_DIR}/include" "${CMAKE_CURRENT_BINARY_DIR}"
 "${infiltratr_common_SOURCE_DIR}/include")
target_link_libraries(ufs1-driver PRIVATE InfiltratrCommon::Common OpenSSL::Crypto)
# A standalone, non-installed Common V2 firmware ELF made from the same
# native UFS1 decoder and V2 callbacks. Publication requires real OVMF reads.
set(UFS1_FIRMWARE_DIR "${CMAKE_CURRENT_BINARY_DIR}/firmware")
set(UFS1_FIRMWARE_ELF "${UFS1_FIRMWARE_DIR}/UFS1.so")
add_custom_command(OUTPUT "${UFS1_FIRMWARE_ELF}"
 COMMAND "${CMAKE_COMMAND}" -S "${CMAKE_CURRENT_SOURCE_DIR}/module/firmware"
  -B "${UFS1_FIRMWARE_DIR}" -DCMAKE_BUILD_TYPE=Release
  "-DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}"
  "-DCOMMON_INCLUDE_DIR=${infiltratr_common_SOURCE_DIR}/include"
  "-DCOMMON_SOURCE_DIR=${infiltratr_common_SOURCE_DIR}"
 COMMAND "${CMAKE_COMMAND}" --build "${UFS1_FIRMWARE_DIR}" --parallel 2
 DEPENDS module/firmware/CMakeLists.txt module/firmware/runtime.c
  native/ufs_native.c module/ufs_module.c
  "${infiltratr_common_SOURCE_DIR}/src/arithmetic.c"
  "${infiltratr_common_SOURCE_DIR}/src/core.c"
  "${infiltratr_common_SOURCE_DIR}/include/infiltratr/filesystem_module_v2.h"
 VERBATIM)
add_custom_target(ufs1-firmware-elf DEPENDS "${UFS1_FIRMWARE_ELF}")
# Stage the same freestanding engine in the installed V2 shared-object carrier.
if(NOT CMAKE_OBJCOPY)
 find_program(CMAKE_OBJCOPY NAMES objcopy llvm-objcopy REQUIRED)
endif()
add_dependencies(ufs1-driver ufs1-firmware-elf)
set_property(TARGET ufs1-driver APPEND PROPERTY LINK_DEPENDS "${UFS1_FIRMWARE_ELF}")
add_custom_command(TARGET ufs1-driver POST_BUILD
 COMMAND "${CMAKE_OBJCOPY}" --add-section
  ".infiltrator_boot=${UFS1_FIRMWARE_ELF}"
  --set-section-flags .infiltrator_boot=readonly
  "$<TARGET_FILE:ufs1-driver>"
 VERBATIM)

if(BUILD_TESTING)
 add_executable(ufs-native-format-test tests/test_format.c)
 target_include_directories(ufs-native-format-test PRIVATE "${infiltratr_common_SOURCE_DIR}/include")
 target_link_libraries(ufs-native-format-test PRIVATE ${CMAKE_DL_LIBS})
 target_compile_options(ufs-native-format-test PRIVATE -Wall -Wextra -Wpedantic -Werror)
 add_test(NAME ufs1-native-format COMMAND sh "${CMAKE_CURRENT_SOURCE_DIR}/tests/format_media.sh" "$<TARGET_FILE:ufs-native-format-test>" "$<TARGET_FILE:ufs1-driver>")
 add_executable(ufs1-module-test tests/test_module.c)
 target_include_directories(ufs1-module-test PRIVATE
   "${CMAKE_CURRENT_SOURCE_DIR}/include"
   "${CMAKE_CURRENT_SOURCE_DIR}/native"
   "${infiltratr_common_SOURCE_DIR}/include")
 target_link_libraries(ufs1-module-test PRIVATE ufs1-driver)
 add_test(NAME ufs1-module-interface COMMAND ufs1-module-test)
 add_test(NAME ufs1-only-common-v2-export
  COMMAND bash "${CMAKE_CURRENT_SOURCE_DIR}/tests/check_v2_exports.sh"
    "$<TARGET_FILE:ufs1-driver>")
endif()
install(TARGETS ufs1-driver LIBRARY DESTINATION /System/Filesystems)

# Build the same current, source-derived manual used by native installer release.
set(UFS1_GENERATED_PDF "${CMAKE_CURRENT_BINARY_DIR}/Filesystem-UFS1.pdf")
add_custom_command(
 OUTPUT "${UFS1_GENERATED_PDF}"
 COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/standalone/generate_manual.py"
         "${CMAKE_CURRENT_SOURCE_DIR}/VERSION"
         "${CMAKE_CURRENT_SOURCE_DIR}/docs/UFS1.pages"
         "${UFS1_GENERATED_PDF}"
 DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION"
         "${CMAKE_CURRENT_SOURCE_DIR}/docs/UFS1.pages"
         "${CMAKE_CURRENT_SOURCE_DIR}/standalone/manual.py"
         "${CMAKE_CURRENT_SOURCE_DIR}/standalone/generate_manual.py"
 VERBATIM)
add_custom_target(ufs1-manual ALL DEPENDS "${UFS1_GENERATED_PDF}")
install(FILES "${UFS1_GENERATED_PDF}"
        DESTINATION /System/Resources/Documentation)
