# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/joaobiu/simsopt_curvecws

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/joaobiu/simsopt_curvecws/cmake-build

# Include any dependencies generated for this target.
include CMakeFiles/profiling.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/profiling.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/profiling.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/profiling.dir/flags.make

CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o: CMakeFiles/profiling.dir/flags.make
CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o: ../src/profiling/profiling.cpp
CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o: CMakeFiles/profiling.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/joaobiu/simsopt_curvecws/cmake-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o -MF CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o.d -o CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o -c /home/joaobiu/simsopt_curvecws/src/profiling/profiling.cpp

CMakeFiles/profiling.dir/src/profiling/profiling.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/profiling.dir/src/profiling/profiling.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/joaobiu/simsopt_curvecws/src/profiling/profiling.cpp > CMakeFiles/profiling.dir/src/profiling/profiling.cpp.i

CMakeFiles/profiling.dir/src/profiling/profiling.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/profiling.dir/src/profiling/profiling.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/joaobiu/simsopt_curvecws/src/profiling/profiling.cpp -o CMakeFiles/profiling.dir/src/profiling/profiling.cpp.s

CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o: CMakeFiles/profiling.dir/flags.make
CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o: ../src/simsoptpp/biot_savart_c.cpp
CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o: CMakeFiles/profiling.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/joaobiu/simsopt_curvecws/cmake-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o -MF CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o.d -o CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o -c /home/joaobiu/simsopt_curvecws/src/simsoptpp/biot_savart_c.cpp

CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/joaobiu/simsopt_curvecws/src/simsoptpp/biot_savart_c.cpp > CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.i

CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/joaobiu/simsopt_curvecws/src/simsoptpp/biot_savart_c.cpp -o CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.s

CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o: CMakeFiles/profiling.dir/flags.make
CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o: ../src/simsoptpp/biot_savart_vjp_c.cpp
CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o: CMakeFiles/profiling.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/joaobiu/simsopt_curvecws/cmake-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Building CXX object CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o -MF CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o.d -o CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o -c /home/joaobiu/simsopt_curvecws/src/simsoptpp/biot_savart_vjp_c.cpp

CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/joaobiu/simsopt_curvecws/src/simsoptpp/biot_savart_vjp_c.cpp > CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.i

CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/joaobiu/simsopt_curvecws/src/simsoptpp/biot_savart_vjp_c.cpp -o CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.s

CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o: CMakeFiles/profiling.dir/flags.make
CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o: ../src/simsoptpp/regular_grid_interpolant_3d_c.cpp
CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o: CMakeFiles/profiling.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/joaobiu/simsopt_curvecws/cmake-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Building CXX object CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o -MF CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o.d -o CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o -c /home/joaobiu/simsopt_curvecws/src/simsoptpp/regular_grid_interpolant_3d_c.cpp

CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/joaobiu/simsopt_curvecws/src/simsoptpp/regular_grid_interpolant_3d_c.cpp > CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.i

CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/joaobiu/simsopt_curvecws/src/simsoptpp/regular_grid_interpolant_3d_c.cpp -o CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.s

# Object files for target profiling
profiling_OBJECTS = \
"CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o" \
"CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o" \
"CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o" \
"CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o"

# External object files for target profiling
profiling_EXTERNAL_OBJECTS =

profiling: CMakeFiles/profiling.dir/src/profiling/profiling.cpp.o
profiling: CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_c.cpp.o
profiling: CMakeFiles/profiling.dir/src/simsoptpp/biot_savart_vjp_c.cpp.o
profiling: CMakeFiles/profiling.dir/src/simsoptpp/regular_grid_interpolant_3d_c.cpp.o
profiling: CMakeFiles/profiling.dir/build.make
profiling: thirdparty/fmt/libfmt.a
profiling: CMakeFiles/profiling.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/joaobiu/simsopt_curvecws/cmake-build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_5) "Linking CXX executable profiling"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/profiling.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/profiling.dir/build: profiling
.PHONY : CMakeFiles/profiling.dir/build

CMakeFiles/profiling.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/profiling.dir/cmake_clean.cmake
.PHONY : CMakeFiles/profiling.dir/clean

CMakeFiles/profiling.dir/depend:
	cd /home/joaobiu/simsopt_curvecws/cmake-build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/joaobiu/simsopt_curvecws /home/joaobiu/simsopt_curvecws /home/joaobiu/simsopt_curvecws/cmake-build /home/joaobiu/simsopt_curvecws/cmake-build /home/joaobiu/simsopt_curvecws/cmake-build/CMakeFiles/profiling.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/profiling.dir/depend

