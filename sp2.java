public enum Role {
    USER,
    ADMIN
}
public enum FoodStatus {
    AVAILABLE,      
    UNAVAILABLE     
}
public enum OrderStatus {
    PENDING,        
    CONFIRMED,     
    PREPARING,     
    DELIVERING,     
    COMPLETED,      
    CANCELLED       
}
@Configuration
@RequiredArgsConstructor
public class DataSeeder {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Bean
    CommandLineRunner seedData() {
        return args -> {

            if (userRepository.count() == 0) {

                User admin = User.builder()
                        .fullName("System Admin")
                        .email("admin@foodorder.com")
                        .password(passwordEncoder.encode("Admin@123"))
                        .role(Role.ADMIN)
                        .build();

                User user1 = User.builder()
                        .fullName("Nguyen Van A")
                        .email("user1@gmail.com")
                        .password(passwordEncoder.encode("User@123"))
                        .role(Role.USER)
                        .build();

                User user2 = User.builder()
                        .fullName("Tran Thi B")
                        .email("user2@gmail.com")
                        .password(passwordEncoder.encode("User@123"))
                        .role(Role.USER)
                        .build();

                User user3 = User.builder()
                        .fullName("Le Van C")
                        .email("user3@gmail.com")
                        .password(passwordEncoder.encode("User@123"))
                        .role(Role.USER)
                        .build();

                userRepository.saveAll(
                        List.of(admin, user1, user2, user3)
                );
            }
        };
    }
}